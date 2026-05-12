from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import CandidateProfile, JobRequirement, CandidateMatch, MatchingAlgorithm, MatchHistory
from .serializers import (
    CandidateProfileSerializer, JobRequirementSerializer, CandidateMatchSerializer,
    MatchingAlgorithmSerializer, MatchHistorySerializer, JobMatchingRequestSerializer,
    CandidateMatchingRequestSerializer, MatchHistoryCreateSerializer
)
from .services import CandidateMatchingService


class CandidateProfileViewSet(viewsets.ModelViewSet):
    queryset = CandidateProfile.objects.all()
    serializer_class = CandidateProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return CandidateProfile.objects.all()
        return CandidateProfile.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def find_matches(self, request, pk=None):
        candidate = self.get_object()
        serializer = CandidateMatchingRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CandidateMatchingService()
            matches = service.find_matches_for_candidate(
                candidate_id=candidate.id,
                limit=serializer.validated_data.get('limit', 10),
                min_score=serializer.validated_data.get('min_score', 0.0),
                filters={
                    'job_types': serializer.validated_data.get('job_types'),
                    'locations': serializer.validated_data.get('locations'),
                    'industries': serializer.validated_data.get('industries')
                }
            )
            
            matches_serializer = CandidateMatchSerializer(matches, many=True)
            return Response(matches_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_all_matches(self, request, pk=None):
        candidate = self.get_object()
        service = CandidateMatchingService()
        matches = service.update_all_matches_for_candidate(candidate.id)
        
        return Response({
            'message': f'Updated {len(matches)} matches for candidate',
            'total_matches': len(matches)
        })


class JobRequirementViewSet(viewsets.ModelViewSet):
    queryset = JobRequirement.objects.all()
    serializer_class = JobRequirementSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def find_candidates(self, request, pk=None):
        job_requirement = self.get_object()
        serializer = JobMatchingRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CandidateMatchingService()
            matches = service.find_matches_for_job(
                job_id=job_requirement.job.id,
                limit=serializer.validated_data.get('limit', 10),
                min_score=serializer.validated_data.get('min_score', 0.0)
            )
            
            matches_serializer = CandidateMatchSerializer(matches, many=True)
            return Response(matches_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_all_matches(self, request, pk=None):
        job_requirement = self.get_object()
        service = CandidateMatchingService()
        matches = service.update_all_matches_for_job(job_requirement.job.id)
        
        return Response({
            'message': f'Updated {len(matches)} matches for job',
            'total_matches': len(matches)
        })


class CandidateMatchViewSet(viewsets.ModelViewSet):
    queryset = CandidateMatch.objects.all()
    serializer_class = CandidateMatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidateMatch.objects.select_related('candidate__user', 'job')
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        job_id = self.request.query_params.get('job_id')
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        min_score = self.request.query_params.get('min_score')
        if min_score:
            queryset = queryset.filter(overall_score__gte=float(min_score))
        
        is_recommended = self.request.query_params.get('is_recommended')
        if is_recommended is not None:
            queryset = queryset.filter(is_recommended=is_recommended.lower() == 'true')
        
        return queryset.order_by('-overall_score')
    
    @action(detail=False, methods=['get'])
    def my_matches(self, request):
        try:
            candidate_profile = request.user.candidate_profile
            matches = self.get_queryset().filter(candidate=candidate_profile)
            
            page = self.paginate_queryset(matches)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(matches, many=True)
            return Response(serializer.data)
        
        except CandidateProfile.DoesNotExist:
            return Response(
                {'error': 'Candidate profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def add_to_history(self, request, pk=None):
        match = self.get_object()
        serializer = MatchHistoryCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            history = MatchHistory.objects.create(
                candidate=match.candidate,
                job=match.job,
                action=serializer.validated_data['action'],
                notes=serializer.validated_data.get('notes', '')
            )
            
            history_serializer = MatchHistorySerializer(history)
            return Response(history_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MatchingAlgorithmViewSet(viewsets.ModelViewSet):
    queryset = MatchingAlgorithm.objects.all()
    serializer_class = MatchingAlgorithmSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        algorithm = self.get_object()
        
        MatchingAlgorithm.objects.filter(is_active=True).update(is_active=False)
        algorithm.is_active = True
        algorithm.save()
        
        return Response({
            'message': f'Activated algorithm: {algorithm.name}',
            'algorithm': MatchingAlgorithmSerializer(algorithm).data
        })


class MatchHistoryViewSet(viewsets.ModelViewSet):
    queryset = MatchHistory.objects.all()
    serializer_class = MatchHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = MatchHistory.objects.select_related('candidate__user', 'job')
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        job_id = self.request.query_params.get('job_id')
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset.order_by('-action_date')
    
    @action(detail=False, methods=['get'])
    def my_history(self, request):
        try:
            candidate_profile = request.user.candidate_profile
            history = self.get_queryset().filter(candidate=candidate_profile)
            
            page = self.paginate_queryset(history)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(history, many=True)
            return Response(serializer.data)
        
        except CandidateProfile.DoesNotExist:
            return Response(
                {'error': 'Candidate profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

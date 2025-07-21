from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Count  
import json
import logging
from .models import SmartPrepSession, create_session_from_ai
from .agent import get_company_prep_advice

logger = logging.getLogger(__name__)

def smart_prep_page(request):
    """Main smart prep page showing existing sessions and search"""
    
    # Get search query
    search_query = request.GET.get('search', '').strip()
    
    # Filter sessions
    sessions = SmartPrepSession.objects.all()
    
    if search_query:
        sessions = sessions.filter(
            Q(company_name__icontains=search_query) | 
            Q(target_role__icontains=search_query)
        )
    
    # Get popular companies (companies with most sessions)
    popular_companies = (SmartPrepSession.objects
                        .values('company_name')
                        .annotate(count=Count('company_name')) 
                        .order_by('-count')[:10])
    
    context = {
        'sessions': sessions[:20],  # Limit to 20 recent sessions
        'search_query': search_query,
        'popular_companies': popular_companies,
        'total_sessions': SmartPrepSession.objects.count(),
    }
    
    return render(request, 'smart_prep/smart_prep.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def create_prep_session(request):
    """Create new preparation session via AJAX"""
    
    try:
        data = json.loads(request.body)
        company_name = data.get('company_name', '').strip()
        target_role = data.get('target_role', 'Software Engineer').strip()
        user_experience = data.get('user_experience', '').strip()
        
        if not company_name:
            return JsonResponse({
                'success': False,
                'error': 'Company name is required'
            }, status=400)
        
        # Check if session already exists for this company/role combo
        existing_session = SmartPrepSession.objects.filter(
            company_name__iexact=company_name,
            target_role__iexact=target_role
        ).first()
        
        if existing_session:
            # DEBUG: Log existing timeline
            logger.info(f"Existing timeline: {existing_session.preparation_timeline}")
            return JsonResponse({
                'success': True,
                'session_id': existing_session.session_id,
                'message': 'Found existing preparation guide',
                'data': {
                    'company_overview': existing_session.company_overview,
                    'key_technologies': existing_session.key_technologies,
                    'preparation_timeline': existing_session.preparation_timeline,
                    'interview_tips': existing_session.interview_tips,
                    'practice_resources': existing_session.practice_resources,
                    'red_flags': existing_session.red_flags,
                }
            })
        
        # Generate new advice using AI
        ai_response = get_company_prep_advice(
            company_name=company_name,
            user_experience=user_experience,
            target_role=target_role
        )
        
        # DEBUG: Log AI response timeline
        logger.info(f"AI timeline response: {ai_response.preparation_timeline}")
        
        # Create session
        session = create_session_from_ai(
            ai_response=ai_response,
            user=request.user if request.user.is_authenticated else None,
            company_name=company_name,
            target_role=target_role
        )
        
        # DEBUG: Log saved timeline
        logger.info(f"Saved timeline: {session.preparation_timeline}")
        
        return JsonResponse({
            'success': True,
            'session_id': session.session_id,
            'message': 'New preparation guide created',
            'data': {
                'company_overview': session.company_overview,
                'key_technologies': session.key_technologies,
                'preparation_timeline': session.preparation_timeline,
                'interview_tips': session.interview_tips,
                'practice_resources': session.practice_resources,
                'red_flags': session.red_flags,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def prep_session_detail(request, session_id):
    """View detailed preparation session"""
    
    try:
        session = SmartPrepSession.objects.get(session_id=session_id)
        
        # DEBUG: Log timeline data
        logger.info(f"Session {session_id} timeline: {session.preparation_timeline}")
        
        context = {
            'session': session,
        }
        
        return render(request, 'smart_prep/session_detail.html', context)
        
    except SmartPrepSession.DoesNotExist:
        messages.error(request, 'Preparation session not found.')
        return redirect('smart-prep')


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Count  
import json
import logging
from .models import SmartPrepSession
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
            return JsonResponse({
                'success': True,
                'session_id': existing_session.session_id,
                'message': 'Found existing preparation guide'
            })
        
        # Generate new advice using AI
        logger.info(f"Generating AI advice for {company_name}")
        ai_response = get_company_prep_advice(
            company_name=company_name,
            user_experience=user_experience,
            target_role=target_role
        )
        
        # Convert timeline to dict BEFORE creating session
        timeline_dict = ai_response.preparation_timeline.to_dict()
        logger.info(f"Converted timeline: {timeline_dict}")
        
        # Create session manually with converted data
        session = SmartPrepSession.objects.create(
            company_name=company_name,
            target_role=target_role,
            company_overview=ai_response.company_overview,
            key_technologies=ai_response.key_technologies,
            preparation_timeline=timeline_dict,  # Use converted dict
            interview_tips=ai_response.interview_tips,
            practice_resources=ai_response.practice_resources,
            red_flags=ai_response.red_flags
        )
        
        # Verify what was saved
        session.refresh_from_db()
        logger.info(f"Saved session {session.session_id} with timeline: {session.preparation_timeline}")
        
        return JsonResponse({
            'success': True,
            'session_id': session.session_id,
            'message': 'New preparation guide created'  
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
            'error': f'Failed to create session: {str(e)}'
        }, status=500)

def prep_session_detail(request, session_id):
    """View detailed preparation session"""
    
    try:
        session = SmartPrepSession.objects.get(session_id=session_id)
        
        # DEBUG: Log timeline data
        logger.info(f"Session {session_id} timeline: {session.preparation_timeline}")
        logger.info(f"Timeline type: {type(session.preparation_timeline)}")
        logger.info(f"Timeline keys: {list(session.preparation_timeline.keys()) if session.preparation_timeline else 'No keys'}")
        
        context = {
            'session': session,
        }
        
        return render(request, 'smart_prep/session_detail.html', context)
        
    except SmartPrepSession.DoesNotExist:
        messages.error(request, 'Preparation session not found.')
        return redirect('smart-prep')


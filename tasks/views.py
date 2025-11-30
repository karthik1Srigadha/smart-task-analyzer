import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .scoring import calculate_task_score, detect_cycle
from datetime import date


@csrf_exempt
def analyze(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        payload = json.loads(request.body)
        tasks = payload if isinstance(payload, list) else payload.get('tasks', [])
    except Exception as e:
        return HttpResponseBadRequest('Invalid JSON')

    # build map with integer ids when possible
    tasks_map = {}
    for idx, t in enumerate(tasks):
        # ensure each task has an id (use provided id or index)
        tid = t.get('id', idx)
        t['id'] = tid
        tasks_map[tid] = t

    # detect cycles
    cycles = detect_cycle(tasks_map)
    if cycles:
        # return helpful info but continue scoring (mark affected tasks)
        cycle_info = [{'cycle': c} for c in cycles]
    else:
        cycle_info = []

    strategy = payload.get('strategy') if isinstance(payload, dict) else None
    # score each
    scored = []
    for t in tasks_map.values():
        score, explanation = calculate_task_score(t, tasks_map=tasks_map, strategy=strategy)
        scored.append({**t, 'score': score, 'explanation': explanation})

    # sort descending
    scored.sort(key=lambda x: x['score'], reverse=True)

    return JsonResponse({'tasks': scored, 'cycles': cycle_info})

def suggest(request):
    # For simplicity: read from GET query 'tasks' as JSON string or static sample if none
    tasks_json = request.GET.get('tasks')
    if not tasks_json:
        return JsonResponse({'error': 'Please pass tasks JSON in ?tasks='}, status=400)
    try:
        tasks = json.loads(tasks_json)
    except:
        return HttpResponseBadRequest('Invalid JSON')

    # reuse analyze logic to score
    payload = {'tasks': tasks, 'strategy': 'smart_balance'}
    r = analyze_simple(payload)
    # r: list sorted tasks
    top3 = r[:3]
    explanations = []
    for t in top3:
        explanations.append({
            'title': t['title'],
            'score': t['score'],
            'why': t.get('explanation', '')
        })
    return JsonResponse({'suggestions': explanations})

# helper so we can call scoring internally
def analyze_simple(payload):
    tasks = payload.get('tasks', [])
    tasks_map = {}
    for idx, t in enumerate(tasks):
        tid = t.get('id', idx)
        t['id'] = tid
        tasks_map[tid] = t
    scored = []
    for t in tasks_map.values():
        score, explanation = calculate_task_score(t, tasks_map=tasks_map, strategy=payload.get('strategy'))
        scored.append({**t, 'score': score, 'explanation': explanation})
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored



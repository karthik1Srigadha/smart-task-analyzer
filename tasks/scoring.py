from datetime import date, datetime
from collections import deque

DEFAULT_IMPORTANCE = 5

def parse_date(d):
    if not d:
        return None
    if isinstance(d, date):
        return d
    # accept ISO strings
    return datetime.strptime(d, "%Y-%m-%d").date()

def detect_cycle(tasks):
    # tasks: dict id -> task_dict (with 'dependencies' list). returns list of cycles or empty
    graph = {tid: set(task.get('dependencies', [])) for tid, task in tasks.items()}
    visited = {}
    cycles = []

    def dfs(node, stack):
        visited[node] = 1
        stack.append(node)
        for nei in graph.get(node, []):
            if nei not in graph:
                continue
            if visited.get(nei, 0) == 0:
                dfs(nei, stack)
            elif visited.get(nei) == 1 and nei in stack:
                idx = stack.index(nei)
                cycles.append(stack[idx:] + [nei])
        stack.pop()
        visited[node] = 2

    for n in graph:
        if visited.get(n, 0) == 0:
            dfs(n, [])
    return cycles

def calculate_task_score(task, tasks_map=None, strategy='smart_balance'):
    """
    task: dict with keys title, due_date (str yyyy-mm-dd), importance (1-10), estimated_hours (int), dependencies (list)
    tasks_map: dict id -> task dict (optional) to check blocked_by_count
    strategy: 'smart_balance' | 'fastest_wins' | 'high_impact' | 'deadline_driven'
    returns: score (higher -> more priority), explanation str
    """
    today = date.today()
    score = 0
    reasons = []

    # normalize
    importance = int(task.get('importance', DEFAULT_IMPORTANCE) or DEFAULT_IMPORTANCE)
    est_hours = int(task.get('estimated_hours', 1) or 1)
    due_date = parse_date(task.get('due_date'))
    deps = task.get('dependencies') or []

    # 1) Urgency
    if due_date:
        days_until = (due_date - today).days
        if days_until < 0:
            score += 200
            reasons.append(f'OVERDUE by {-days_until} day(s)')
        elif days_until <= 1:
            score += 120
            reasons.append('due within 1 day')
        elif days_until <= 3:
            score += 60
            reasons.append('due within 3 days')
        else:
            # less urgent as days increase (small bonus if due within 14 days)
            if days_until <= 14:
                score += 20
    else:
        # no date -> neutral small penalty (if you want to prefer dated tasks)
        score += 0

    # 2) Importance (weighted)
    score += importance * 10
    reasons.append(f'importance {importance}')

    # 3) Effort (quick wins)
    if est_hours <= 1:
        score += 30
        reasons.append('quick win (<1h)')
    elif est_hours <= 3:
        score += 10
        reasons.append('short task (<=3h)')
    else:
        # big tasks get smaller bonus
        score += max(0, 5 - (est_hours - 3))  # small diminishing

    # 4) Dependencies: tasks blocking more tasks are higher priority
    blocked_count = 0
    if tasks_map:
        # count how many tasks list this task's id in dependencies
        tid = task.get('id')
        if tid is not None:
            for other in tasks_map.values():
                if tid in (other.get('dependencies') or []):
                    blocked_count += 1
    score += blocked_count * 25
    if blocked_count:
        reasons.append(f'blocks {blocked_count} task(s)')

    # 5) Strategy adjustments
    strategy = strategy or 'smart_balance'
    if strategy == 'fastest_wins':
        # boost low effort
        if est_hours <= 3:
            score += 40
            reasons.append('strategy: fastest_wins boost')
    elif strategy == 'high_impact':
        # emphasize importance heavily
        score += importance * 15
        reasons.append('strategy: high_impact boost')
    elif strategy == 'deadline_driven':
        if due_date:
            # convert days into inverse
            days_until = (due_date - today).days
            score += max(0, 100 - days_until)  # more weight to nearer deadlines
            reasons.append('strategy: deadline_driven applied')

    explanation = "; ".join(reasons)
    return score, explanation

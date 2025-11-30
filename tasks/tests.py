from django.test import TestCase
from tasks.scoring import calculate_task_score


class ScoringTests(TestCase):
    def test_overdue_high_score(self):
        task = {"id":0, "title":"old", "due_date":"2020-01-01", "importance":5, "estimated_hours":2}
        score, _ = calculate_task_score(task, tasks_map={0:task})
        self.assertTrue(score > 150)

    def test_quick_win(self):
        task = {"id":1, "title":"small", "due_date":None, "importance":3, "estimated_hours":1}
        score, _ = calculate_task_score(task, tasks_map={1:task})
        self.assertTrue(score > 30)

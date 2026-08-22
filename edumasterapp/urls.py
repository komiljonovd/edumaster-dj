from django.urls import path
from .views import (
    course_views,
    lesson_views,
    quiz_views,
    question_views,
    assignment_views,
    assignment_sub_views,
    payment_views,
    quizzes,
    report_views,
    certificate_views,
)

urlpatterns = [
    path(
        "course/", course_views.CourseListCreateAPI.as_view(), name="course-list-create"
    ),
    path(
        "course/<int:pk>/", course_views.CourseDetailApi.as_view(), name="course-detail"
    ),
    path("lesson/", lesson_views.LessonCreateAPI.as_view(), name="lesson-create"),
    path(
        "lesson/<int:pk>/", lesson_views.LessonDetailAPI.as_view(), name="lesson-detail"
    ),
    path("quiz/", quiz_views.QuizListCreateAPI.as_view(), name="quiz-list-create"),
    path("quiz/<int:pk>/", quiz_views.QuizDetailAPI.as_view(), name="quiz-detail"),
    path(
        "question/", question_views.QuestionCreateAPI.as_view(), name="question-create"
    ),
    path(
        "question/<int:pk>/",
        question_views.QuestionDetailAPI.as_view(),
        name="question-detail",
    ),
    path(
        "assignment/",
        assignment_views.AssignmentListCreateAPI.as_view(),
        name="assignment-list-create",
    ),
    path(
        "assignment/<int:pk>/",
        assignment_views.AssignmentDetailAPI.as_view(),
        name="assignment-detail",
    ),
    path(
        "assignment/student/",
        assignment_sub_views.StudentCreateAssignmentAPI.as_view(),
        name="student-assignment-create",
    ),
    path(
        "assignment/student/<int:pk>/",
        assignment_sub_views.StudentUpdateAssignmentAPI.as_view(),
        name="student-assignment-update",
    ),
    path(
        "assignment/teacher/<int:pk>/",
        assignment_sub_views.TeacherAssignmentSubDetailAPI.as_view(),
        name="teacher-assignment-detail",
    ),
    path(
        "payment/", payment_views.PaymentListCreateAPI.as_view(), name="payment-create"
    ),
    path(
        "payment/<int:pk>/",
        payment_views.PaymentDetailAPI.as_view(),
        name="payment-detail",
    ),
    # QUIZ
    path(
        "quiz-test/<int:quiz_id>/",
        quizzes.QuizDetailAPIView.as_view(),
        name="quiz-detail",
    ),
    path(
        "quiz-test/<int:quiz_id>/start/",
        quizzes.QuizStartAPIView.as_view(),
        name="quiz-start",
    ),
    path(
        "quiz-test/<int:quiz_id>/questions/",
        quizzes.QuizQuestionsAPIView.as_view(),
        name="quiz-questions",
    ),
    path(
        "quiz-test/<int:quiz_id>/submit/",
        quizzes.QuizSubmitAPIView.as_view(),
        name="quiz-submit",
    ),
    path(
        "quiz-test/<int:quiz_id>/history/",
        quizzes.QuizAttemptHistoryAPIView.as_view(),
        name="quiz-history",
    ),
    # report for PARENT
    path(
        "parent/children-report/",
        report_views.ParentChildrenReportAPIView.as_view(),
        name="children-report",
    ),
    path(
        "certificate/",
        certificate_views.CertificateListAPI.as_view(),
        name="certificate-list",
    ),
    path(
        "certificate/<uuid:certificate_number>/",
        certificate_views.CertificateDetailAPI.as_view(),
        name="certificate-detail",
    ),
]

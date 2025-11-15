from rest_framework import serializers
from .models import WritingPracticeSession, WritingTypeTaskModel, WritingAnswerModel

class UploadQuestionSerializer(serializers.ModelSerializer):
    total_task1_questions = serializers.SerializerMethodField()
    total_task2_questions = serializers.SerializerMethodField()
    class Meta:
        model = WritingTypeTaskModel
        fields= ["id","number","question_text","image","task","exam_type","total_task1_questions","total_task2_questions"]
        read_only_fields= ['id']
  
    def get_total_task1_questions(self,obj):
        return WritingTypeTaskModel.objects.filter(task="task1").count()
    def get_total_task2_questions(self,obj):
        return WritingTypeTaskModel.objects.filter(task="task2").count()
    




class PracticeExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingTypeTaskModel
        fields = "__all__"


class WritingPracticeSessionSerializer(serializers.ModelSerializer):
    task1_data = PracticeExamSerializer(source="task1", read_only=True)
    task2_data = PracticeExamSerializer(source="task2", read_only=True)

    class Meta:
        model = WritingPracticeSession
        fields = [
            "session_id",
            "exam_type",
            "start_time",
            "end_time",
            "task1_data",
            "task2_data"
        ]

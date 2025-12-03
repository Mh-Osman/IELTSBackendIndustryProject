from rest_framework import serializers
from .models import WritingTypeTask

class WritingTypeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingTypeTask
        fields = "__all__"
        read_only_fields = ("id",)

    def validate(self, data):
      
        writing_task = data.get(
            "writing_task",
            getattr(self.instance, "writing_task", None)
        )
        image = data.get(
            "image",
            getattr(self.instance, "image", None)
        )

        if writing_task == "task1" and not image:
            raise serializers.ValidationError({"image": "Image is required for Task 1."})
        return data

    def create(self, validated_data):
        instance = WritingTypeTask(**validated_data)
        instance.full_clean()
        instance.save()
        return instance

    def update(self, instance, validated_data):
      
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
       
        instance.full_clean()
        instance.save()
        return instance

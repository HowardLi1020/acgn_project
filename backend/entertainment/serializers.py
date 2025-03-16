from rest_framework import serializers
from .models import Game, Animation, Movie

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class AnimationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animation
        fields = '__all__'

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

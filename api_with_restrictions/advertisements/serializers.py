from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        print(data.get('status', None))

        # Проверка на количество открытых объявлений только при создании
        if self.context['request'].method == 'POST':
            if data.get('status') == 'OPEN' and Advertisement.objects.filter(status='OPEN', creator=self.context[
                "request"].user).count() >= 10:
                raise ValidationError('Count adv status=OPEN 10')

        # Проверка на количество открытых объявлений только при обновлении
        if self.context['request'].method == 'PATCH':
            if data.get('status') == 'OPEN' and Advertisement.objects.filter(status='OPEN', creator=self.context[
                "request"].user).count() >= 10:
                raise ValidationError('Count adv status=OPEN 10')

        return data

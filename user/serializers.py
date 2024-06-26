from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
from rest_framework.validators import UniqueTogetherValidator

from user.models import User, UserFollowing


class FollowingSerializer(serializers.ModelSerializer):
    user_id = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="email",
        queryset=User.objects.all(),
    )
    following_user_id = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="email",
        queryset=User.objects.all(),
    )

    class Meta:
        model = UserFollowing
        fields = ("id", "user_id", "following_user_id", "created")
        read_only_fields = ("created", "user_id")
        validators = [
            UniqueTogetherValidator(
                queryset=UserFollowing.objects.all(),
                fields=["user_id", "following_user_id"],
            )
        ]


class FollowersSerializer(serializers.ModelSerializer):
    user_id = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field="email",
        queryset=User.objects.all(),
    )

    class Meta:
        model = UserFollowing
        fields = ("id", "user_id", "created")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "nickname",
            "date_of_birth",
            "biography",
            "profile_image",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise serializers.ValidationError(msg, code="authorization")
            else:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _("Must include 'username' and 'password'.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs

import requests
from django.conf import settings
import requests
from django.conf import settings
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    SendMessageSerializer,
)


@extend_schema_view(
    list=extend_schema(description="List user's conversations."),
    create=extend_schema(description="Create a new conversation."),
    retrieve=extend_schema(description="Get conversation with all messages.", responses={200: ConversationDetailSerializer}),
    destroy=extend_schema(description="Delete a conversation.")
)
class ConversationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """ViewSet for Conversations."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
        return Conversation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        request=SendMessageSerializer,
        responses={201: MessageSerializer(many=True), 404: OpenApiResponse(description="Conversation not found")},
        description="Send a message in a conversation and get AI response."
    )
    @action(detail=True, methods=['post'], url_path='messages')
    def send_message(self, request, pk=None):
        try:
            conversation = self.get_object()
        except Conversation.DoesNotExist:
            return Response({'detail': 'Conversation non trouvée.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_content = serializer.validated_data['content']

        # Save the user's message
        user_message = Message.objects.create(
            conversation=conversation,
            sender=Message.Sender.USER,
            content=user_content,
        )

        # Build context from conversation history
        history = conversation.messages.all().values_list('sender', 'content')
        messages_context = [{'role': sender, 'content': content} for sender, content in history]

        # Build user profile context
        user = request.user
        user_profile = {
            'name': user.get_full_name(),
            'university': user.university,
            'field_of_study': user.field_of_study,
            'bio': user.bio,
        }

        # Call AI service
        ai_response_text = "Je suis l'assistant Smart PFE. Je peux vous aider à trouver des idées de projets de PFE. Pouvez-vous me dire quel domaine vous intéresse ?"
        ai_metadata = {}

        try:
            ai_service_url = getattr(settings, 'AI_SERVICE_URL', 'http://localhost:8001')
            response = requests.post(
                f"{ai_service_url}/api/chat",
                json={'message': user_content, 'context': messages_context, 'user_profile': user_profile},
                timeout=30,
            )
            if response.status_code == 200:
                ai_data = response.json()
                ai_response_text = ai_data.get('response', ai_response_text)
                ai_metadata = ai_data.get('metadata', {})
        except requests.exceptions.RequestException:
            pass

        # Save the AI response
        assistant_message = Message.objects.create(
            conversation=conversation,
            sender=Message.Sender.ASSISTANT,
            content=ai_response_text,
            metadata=ai_metadata,
        )

        # Update conversation title on first message
        if conversation.messages.count() <= 2:
            conversation.title = user_content[:80]
            conversation.save()

        return Response({
            'user_message': MessageSerializer(user_message).data,
            'assistant_message': MessageSerializer(assistant_message).data,
        }, status=status.HTTP_201_CREATED)

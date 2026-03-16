import requests
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    SendMessageSerializer,
)


class ConversationListCreateView(generics.ListCreateAPIView):
    """List user's conversations or create a new one."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConversationDetailView(generics.RetrieveDestroyAPIView):
    """Get conversation with all messages, or delete it."""
    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)


class SendMessageView(APIView):
    """Send a message in a conversation and get AI response."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            conversation = Conversation.objects.get(pk=pk, user=request.user)
        except Conversation.DoesNotExist:
            return Response(
                {'detail': 'Conversation non trouvée.'},
                status=status.HTTP_404_NOT_FOUND,
            )

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
        messages_context = [
            {'role': sender, 'content': content}
            for sender, content in history
        ]

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
                json={
                    'message': user_content,
                    'context': messages_context,
                    'user_profile': user_profile,
                },
                timeout=30,
            )
            if response.status_code == 200:
                ai_data = response.json()
                ai_response_text = ai_data.get('response', ai_response_text)
                ai_metadata = ai_data.get('metadata', {})
        except requests.exceptions.RequestException:
            # AI service unavailable — use fallback
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

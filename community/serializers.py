from collections import Counter
import re
from rest_framework import serializers
from community.models import Community, CommunityPost
from community.serializer_min import CommunityPostSerializerMin
from roles.serializers import RoleSerializerMin
from users.models import UserProfile
from bodies.models import Body
from locations.models import Location
from unicodedata import name

class CommunitySerializers(serializers.ModelSerializer):

    followers_count = serializers.SerializerMethodField()
    is_user_following = serializers.SerializerMethodField()
    roles = RoleSerializerMin(many=True, read_only=True, source='body.roles')
    posts = serializers.SerializerMethodField()


    def get_posts(self, obj):
        """Get the posts of the community """
        queryset = obj.posts.filter(thread_rank=1)
        return CommunityPostSerializerMin(queryset, many=True).data

    def get_followers_count(self, obj):
        """Get followers of body."""
        if obj.body == None:
            return 0
        return obj.body.followers.count()

    def get_is_user_following(self, obj):
        """Get the current user's reaction on the community post """
        request = self.context['request'] if 'request' in self.context else None
        if request and request.user.is_authenticated:
            profile = request.user.profile
            return profile.followed_bodies.filter(id=obj.body.id).exists()
        return False

    class Meta:
        model = Community
        fields = ('id', 'str_id', 'name', 'about', 'description', 'created_at', 'updated_at',
                  'cover_image', 'logo_image', 'followers_count', 'is_user_following', 'roles', 'posts')

    @staticmethod
    def setup_eager_loading(queryset, request):
        """Perform necessary eager loading of data."""

        # Prefetch body child relations

        # Annotate followers count

        return queryset


class CommunityPostSerializers(CommunityPostSerializerMin):
    comments = CommunityPostSerializerMin(many=True)
   
    class Meta:
        model = CommunityPost
        fields = ('id', 'str_id', 'content', 'posted_by',
                  'reactions_count', 'user_reaction', 'comments_count', 'time_of_creation', 'time_of_modification',
                  'image_url', 'comments')

    def create(self,validated_data):
        validated_data["status"]=0
        if validated_data["parent"]:
            validated_data["thread_rank"]=self.context["parent"].thread_rank +1
        else :
            validated_data["thread_rank"]=1
        if validated_data["tag_user_call"]:
                 validated_data["tag_user_call"]=UserProfile.objects.get(name)                
        if validated_data["tag_body_call"]:
                 validated_data["tag_body_call"]=Body.objects.get(name) 
        if validated_data["tag_location_call"]:
                 validated_data["tag_location_call"]=Location.objects.get(name)
        return super().create(validated_data)
    
    def update(self,validated_data,pk):
        if validated_data["tag_user_call"]:
                 validated_data["tag_user_call"]=UserProfile.objects.get(name)                
        if validated_data["tag_body_call"]:
                 validated_data["tag_body_call"]=Body.objects.get(name) 
        if validated_data["tag_location_call"]:
                 validated_data["tag_location_call"]=Location.objects.get(name)
        return super().update(validated_data,pk)

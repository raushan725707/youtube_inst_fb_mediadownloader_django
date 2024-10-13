from django.urls import path
from .views import test_view
from .views import download_video,get_video_formats
from .views import download_video_based_on_format,video_thub_quality,download_video_demo,get_video_info
from .views import instagram_media_handler,download_video_final,download_facebook_video,get_facebook_video_info
from .views import download_image_from_url

urlpatterns = [
    path('test/', test_view, name='test_view'),
       path('download/', download_video, name='download_video'),
       path('formats/', get_video_formats, name='get_video_formats'),
       path('download_format/', download_video_based_on_format, name='download_video_based_on_format'),
       path('thubquality/', video_thub_quality, name='video_thub_quality'),
       path('demodownload/', download_video_demo, name='download_video_demo'),
                      path('getvideoinfo/', get_video_info, name='get_video_info'),
                         path('instagram/media/', instagram_media_handler, name='instagram_media_handler'),
                      path('downloadvideo/', download_video_final, name='download_video_final'),
                     path('download_facebook_video/', download_facebook_video, name='download_facebook_video'),
                     path('facebook_video_info/', get_facebook_video_info, name='get_facebook_video_info'),
                     path('download_image_from_url/', download_image_from_url, name='download_image_from_url'),


]

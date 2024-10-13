import os
import re
import logging
from django.http import JsonResponse, FileResponse,HttpResponse
import yt_dlp
from django.views.decorators.http import require_http_methods

import requests
# Set up logging
logging.basicConfig(level=logging.DEBUG)


def test_view():
    return JsonResponse({'message': 'Hello, world!'})
def sanitize_filename(filename):
    """Sanitize the filename by removing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename).strip()[:255]

def download_video(request):
    """Download a video from the provided URL."""
    video_url = request.GET.get('url')

    if not video_url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            title = info_dict.get('title', "downloaded_video")
            sanitized_title = sanitize_filename(title)
            filename = f"{sanitized_title}.{info_dict['ext']}"
            filepath = os.path.join(os.getcwd(), filename)

            if not os.path.exists(filepath):
                return JsonResponse({'error': 'File was not downloaded successfully.'}, status=500)

            return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def get_video_formats(request):
    """Get available formats for the provided video URL."""
    video_url = request.GET.get('url')

    if not video_url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])
            return JsonResponse({'formats': formats}, status=200)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def download_video_based_on_format(request):
    """Download a video based on the selected format."""
    video_url = request.GET.get('url')
    format_id = request.GET.get('format')

    if not video_url or not format_id:
        return JsonResponse({'error': 'URL or format not provided'}, status=400)

    ydl_opts = {
        'format': format_id,
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            title = info_dict.get('title', "downloaded_video")
            sanitized_title = sanitize_filename(title)
            filename = f"{sanitized_title}.{info_dict['ext']}"
            filepath = os.path.join(os.getcwd(), filename)

            if not os.path.exists(filepath):
                return JsonResponse({'error': 'File was not downloaded successfully.'}, status=500)

            return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def video_thub_quality(request):
    """Placeholder method for getting video thumbnail quality (to be implemented)."""
    # This function can be expanded based on your requirements
    return JsonResponse({'message': 'Video thumbnail quality function not implemented yet.'}, status=501)

def download_video_demo(request):
    video_url = request.GET.get('url')
    format_id = request.GET.get('format')  # Get the format from the request
    if not video_url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    ydl_opts = {
        'format': format_id or 'best',  # Use the selected format or default to 'best'
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            title = info_dict.get('title', None)
            ext = info_dict['ext']

            # Generate the base filename
            base_filename = f"{title}.{ext}"
            filepath = os.path.join(os.getcwd(), base_filename)

            # Check for existing files and modify filename if needed
            if os.path.exists(filepath):
                base, extension = os.path.splitext(base_filename)
                counter = 1
                while os.path.exists(filepath):
                    filepath = os.path.join(os.getcwd(), f"{base} ({counter}){extension}")
                    counter += 1

            # Open the file and send it as a response
            response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=os.path.basename(filepath))
            return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    


def get_video_info(request):
    video_url = request.GET.get('url')
    if not video_url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    ydl_opts = {
        'format': 'best',  # We only need info, not the actual download
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)

            # Extract required information
            print("info_dict",info_dict)
            thumbnail = info_dict.get('thumbnail', None)
            duration = info_dict.get('duration', None)  # Duration in seconds
            title = info_dict.get('title', None)
            filesize=info_dict.get('filesize', None)


            # Available formats
            available_formats = []
            for fmt in info_dict.get('formats', []):
                if 'height' in fmt and 'ext' in fmt:
                    available_formats.append({
                        'format': fmt['format'],
                        'height': fmt['height'],
                        'ext': fmt['ext'],
                         'filesize': filesize,
                    })

            # Filter to include only specific resolutions
            resolution_options = [144, 240, 360, 480, 720, 1080, 2160, 4320]  # 4K and 8K are 2160 and 4320 respectively
            filtered_formats = [
                fmt for fmt in available_formats if fmt['height'] in resolution_options
            ]

            response_data = {
                'thumbnail': thumbnail,
                'duration': duration,
                'title': title,
                'available_formats': filtered_formats,
            }

            return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)    
#  # Reusing the download_video function for demo




#instagram handler
@require_http_methods(["GET"])
def instagram_media_handler(request):
    instagram_url = request.GET.get('url')  # Corrected from Get to GET

    if not instagram_url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,  # Get metadata without downloading
        'geo_bypass': True,    # Bypass geo-restrictions if applicable
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(instagram_url)

            # Check if the URL points to a profile or media
            if 'entries' in info_dict:  # If it's a playlist or multiple entries
                entries = info_dict['entries']
                media_info = [{'title': entry.get('title'), 'url': entry.get('url')} for entry in entries]
                return JsonResponse({'media': media_info})

            # If it's a single video or reel
            if 'title' in info_dict:
                title = info_dict.get('title')
                media_type = info_dict.get('extractor')
                
                if media_type in ['instagram', 'instagram:video', 'instagram:reel']:
                    download_info = {
                        'title': title,
                        'url': info_dict.get('url'),
                        'thumbnail': info_dict.get('thumbnail'),
                        'duration': info_dict.get('duration'),
                        'formats': []
                    }

                    # Fetch available formats
                    for format_info in info_dict.get('formats', []):
                        if format_info.get('filesize'):
                            download_info['formats'].append({
                                'format': format_info.get('format'),
                                'height': format_info.get('height'),
                                'ext': format_info.get('ext'),
                                'filesize': format_info.get('filesize'),
                            })

                    return JsonResponse(download_info)

                else:
                    return JsonResponse({'error': 'This media cannot be downloaded.'}, status=403)

            return JsonResponse({'error': 'Unable to extract media information.'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





@require_http_methods(["GET"])
def download_video_final(request):
    instagram_url = request.GET.get('url')
    format_choice = request.GET.get('format')

    if not instagram_url or not format_choice:
        return JsonResponse({'error': 'No URL or format provided'}, status=400)

    ydl_opts = {
        'format': format_choice,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Optional: If you want audio as well
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',  # Save the file with the title as the filename
        'skip_download': False,  # We want to download the file
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(instagram_url, download=True)
            filename = ydl.prepare_filename(info_dict)  # Get the actual file path

        # Open the file for downloading
        with open(filename, 'rb') as file:
            response = HttpResponse(file.read(), content_type='video/mp4')  # Change to the appropriate content type
            response['Content-Disposition'] = f'attachment; filename="{info_dict["title"]}.{info_dict["ext"]}"'
            return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  



#Facebook
@require_http_methods(["GET"])
def get_facebook_video_info(request):
    facebook_url = request.GET.get('url')

    if not facebook_url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    ydl_opts = {
        'quiet': True,
        'skip_download': True,  # Only get metadata
        'extract_flat': True,   # This allows us to get the formats
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(facebook_url)
            formats = info_dict.get('formats', [])
            available_formats = [{'format': f.get('format_id'), 'height': f.get('height'), 'ext': f.get('ext')} for f in formats if f.get('height')]

        return JsonResponse({'formats': available_formats})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





@require_http_methods(["GET"])
def download_facebook_video(request):
    facebook_url = request.GET.get('url')

    if not facebook_url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    ydl_opts = {
        'quiet': True,
        'outtmpl': '%(title)s.%(ext)s',
        'skip_download': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(facebook_url, download=True)
            filename = ydl.prepare_filename(info_dict)

        # Open the file for downloading
        with open(filename, 'rb') as file:
            response = HttpResponse(file.read(), content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{info_dict["title"]}.{info_dict["ext"]}"'
            return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# @require_http_methods(["GET"])
# def download_facebook_video(request):
#     facebook_url = request.GET.get('url')

#     if not facebook_url:
#         return JsonResponse({'error': 'No URL provided'}, status=400)

#     ydl_opts = {
#         'quiet': True,
#         'outtmpl': '%(title)s.%(ext)s',  # Save the file with the title as the filename
#         'skip_download': False,  # We want to download the file
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info_dict = ydl.extract_info(facebook_url, download=True)
#             filename = ydl.prepare_filename(info_dict)  # Get the actual file path

#         # Open the file for downloading
#         with open(filename, 'rb') as file:
#             response = HttpResponse(file.read(), content_type='video/mp4')  # Change to the appropriate content type
#             response['Content-Disposition'] = f'attachment; filename="{info_dict["title"]}.{info_dict["ext"]}"'
#             return response

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)



@require_http_methods(["GET"])
def download_image_from_url(request):
    image_url = request.GET.get('url')

    if not image_url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    try:
        # Fetch the image
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error for bad responses
        content_type = response.headers.get('Content-Type', '')
        if 'image/jpeg' in content_type:
            file_extension = 'jpg'
        elif 'image/png' in content_type:
            file_extension = 'png'
        elif 'image/gif' in content_type:
            file_extension = 'gif'
        else:
            file_extension = 'jpg'  # Default to jpg if unknown

        # Create a HTTP response with the image
        http_response = HttpResponse(response.content, content_type=content_type)
        http_response['Content-Disposition'] = f'attachment; filename="downloaded_image.{file_extension}"'  # Set filename

        return http_response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
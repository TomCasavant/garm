from flask import Blueprint, request, jsonify, make_response
from garm.db import get_db
from garm.steam_platform import SteamPlatform

bp = Blueprint('base', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def base():
    db = get_db()
    steam_platform = SteamPlatform()

    # {'response': {'total': 927, 'startindex': 1, 'publishedfiledetails': [{'result': 1, 'publishedfileid': '3387591110', 'creator': '76561198057202734', 'creator_appid': 760, 'consumer_appid': 730, 'consumer_shortcutid': 0, 'filename': '730/screenshots/20241219200514_1.jpg', 'file_size': '226215', 'preview_file_size': '15030', 'file_url': 'https://steamuserimages-a.akamaihd.net/ugc/62585168909075911/ECB3FC315F3092E15F5EE1D7CAECD84DE5363D8E/', 'preview_url': 'https://steamuserimages-a.akamaihd.net/ugc/62585168909075940/32E3F8CC2DFC7E374700176FAC35BE7CD41B9656/', 'url': '', 'hcontent_file': '62585168909075911', 'hcontent_preview': '62585168909075940', 'title': '', 'short_description': '', 'time_created': 1734656716, 'time_updated': 1734656716, 'visibility': 0, 'flags': 1536, 'workshop_file': False, 'workshop_accepted': False, 'show_subscribe_all': False, 'num_comments_developer': 0, 'num_comments_public': 0, 'banned': False, 'ban_reason': '', 'banner': '76561197960265728', 'can_be_deleted': True, 'app_name': 'Counter-Strike 2', 'file_type': 5, 'can_subscribe': False, 'subscriptions': 0, 'favorited': 0, 'followers': 0, 'lifetime_subscriptions': 0, 'lifetime_favorited': 0, 'lifetime_followers': 0, 'lifetime_playtime': '0', 'lifetime_playtime_sessions': '0', 'views': 1, 'image_width': 1280, 'image_height': 800, 'image_url': 'https://steamuserimages-a.akamaihd.net/ugc/62585168909075911/ECB3FC315F3092E15F5EE1D7CAECD84DE5363D8E/', 'num_children': 0, 'num_reports': 0, 'vote_data': {'score': 0, 'votes_up': 0, 'votes_down': 0}, 'language': 0, 'maybe_inappropriate_sex': False, 'maybe_inappropriate_violence': False, 'revision_change_number': '0', 'revision': 1, 'ban_text_check_result': 5}, {'result': 1, 'publishedfileid': '3386414931', 'creator': '76561198057202734', 'creator_appid': 760, 'consumer_appid': 379430, 'consumer_shortcutid': 0, 'filename': '379430/screenshots/20241216191442_1.jpg', 'file_size': '128602', 'preview_file_size': '9245', 'file_url': 'https://steamuserimages-a.akamaihd.net/ugc/62585004434150324/D66445CD211DC3371C12C479D9EAC773F8641E6F/', 'preview_url': 'https://steamuserimages-a.akamaihd.net/ugc/62585004434150376/C5F6B767CCD46B6B37CB3E18773A2B704BF38B38/', 'url': '', 'hcontent_file': '6258500443
    screenshots = steam_platform.get_screenshots()
    # Display a webpage with the top 5 screenshots
    # Display game name followed by <img src=preview_url> for each screenshot

    html = "<html><head><title>Top 5 Screenshots</title></head><body>"
    for screenshot in screenshots['response']['publishedfiledetails'][:5]:
        html += f"<h1>{screenshot['app_name']}</h1>"
        html += f"<img src={screenshot['preview_url']}><br>"
    html += "</body></html>"
    return make_response(html, 200)
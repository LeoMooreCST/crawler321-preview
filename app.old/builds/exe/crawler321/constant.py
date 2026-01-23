from enum import Enum

class StatusCode(Enum):
    CONTINUE = 100
    SWTICHING_PROTOCOLS = 101
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    UNUSED = 306
    TEMPORY_REDIRECT = 307
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIME_OUT = 408
    CONFILICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    REQUEST_ENTITY_TOO_LARGE = 413
    REQUEST_URL_TOO_LARGE = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    REQUEST_RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    TOOMANYREQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAG_GETWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIME_OUT = 504
    HTPP_VERSION_NOT_SUPPORTED = 505

# headers simulations
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 '
                  'Safari/537.36',
    "Connection": "close"
}

# default charset
DEFAULT_CHARSET = "UTF-8"
# Spark LLM Config
'''
                                   SPARKAI_URL                  SPARKAI_DOMAIN
    Spark4.0 Ultra  wss://spark-api.xf-yun.com/v4.0/chat        4.0Ultra
    Spark Max       wss://spark-api.xf-yun.com/v3.5/chat       generalv3.5
    Spark Pro-128K  wss://spark-api.xf-yun.com/chat/pro-128k    pro-128k
    Spark Pro       wss://spark-api.xf-yun.com/v3.1/chat        generalv3
    Spark V2.0      wss://spark-api.xf-yun.com/v2.1/chat        generalv2
    Spark Lite      wss://spark-api.xf-yun.com/v1.1/chat        general   [免费]
 
        
'''
SPARK_CONFIG = {
    "Spark/Lite": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v1.1/chat",
        "SPARKAI_DOMAIN": "general"
        },
    "Spark/V2.0": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v2.1/chat",
        "SPARKAI_DOMAIN": "generalv2"
        },
    "Spark/Pro": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v3.1/chat",
        "SPARKAI_DOMAIN": "generalv3"
        },
    "Spark/Pro-128K": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/chat/pro-128k",
        "SPARKAI_DOMAIN": "pro-128k"
        },
    "Spark/Max": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v3.5/chat",
        "SPARKAI_DOMAIN": "generalv3.5"
        },
    "Spark/4.0Ultra": {
        "SPARKAI_URL": "wss://spark-api.xf-yun.com/v4.0/chat",
        "SPARKAI_DOMAIN": "4.0Ultra"
        }
}
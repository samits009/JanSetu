class ApiException implements Exception {
  final String message;
  final String? messageHi;
  final int? statusCode;
  final dynamic details;

  ApiException({
    required this.message,
    this.messageHi,
    this.statusCode,
    this.details,
  });

  String localizedMessage(String lang) {
    if (lang == 'hi' && messageHi != null && messageHi!.isNotEmpty) {
      return messageHi!;
    }
    return message;
  }

  @override
  String toString() => 'ApiException(status: $statusCode, message: $message)';

  factory ApiException.fromStatusCode(int statusCode, {String? detail, dynamic raw}) {
    switch (statusCode) {
      case 400:
        return BadRequestException(detail ?? 'Invalid request parameters', raw: raw);
      case 401:
        return UnauthorizedException(detail ?? 'Authentication required or session expired', raw: raw);
      case 403:
        return ForbiddenException(detail ?? 'You do not have permission to perform this action', raw: raw);
      case 404:
        return NotFoundException(detail ?? 'Requested citizen resource was not found', raw: raw);
      case 409:
        return ConflictException(detail ?? 'A record with these details already exists', raw: raw);
      case 422:
        return ValidationException(detail ?? 'Please check the entered values', raw: raw);
      case 429:
        return RateLimitException(detail ?? 'Too many requests. Please wait a moment', raw: raw);
      case 500:
      case 502:
      case 503:
        return ServerException(detail ?? 'JanSetu sovereign server encountered an issue', raw: raw);
      default:
        return ApiException(
          statusCode: statusCode,
          message: detail ?? 'Unexpected server response ($statusCode)',
          details: raw,
        );
    }
  }

  factory ApiException.networkError() {
    return NetworkException('No internet connectivity. Please check your network.');
  }

  factory ApiException.timeout() {
    return TimeoutException('Connection to JanSetu server timed out. Please retry.');
  }
}

class NetworkException extends ApiException {
  NetworkException(String message)
      : super(
          message: message,
          messageHi: 'इंटरनेट कनेक्शन नहीं है। कृपया अपना नेटवर्क जांचें।',
          statusCode: 0,
        );
}

class TimeoutException extends ApiException {
  TimeoutException(String message)
      : super(
          message: message,
          messageHi: 'सर्वर से संपर्क का समय समाप्त हो गया। कृपया पुनः प्रयास करें।',
          statusCode: 408,
        );
}

class UnauthorizedException extends ApiException {
  UnauthorizedException(String message, {dynamic raw})
      : super(
          message: message,
          messageHi: 'सत्र समाप्त हो गया है। कृपया पुनः लॉगिन करें।',
          statusCode: 401,
          details: raw,
        );
}

class ForbiddenException extends ApiException {
  ForbiddenException(String message, {dynamic raw})
      : super(
          message: message,
          messageHi: 'आपको इस कार्रवाई की अनुमति नहीं है।',
          statusCode: 403,
          details: raw,
        );
}

class NotFoundException extends ApiException {
  NotFoundException(String message, {dynamic raw})
      : super(
          message: message,
          messageHi: 'अनुरोधित संसाधन उपलब्ध नहीं है।',
          statusCode: 404,
          details: raw,
        );
}

class ConflictException extends ApiException {
  ConflictException(String message, {dynamic raw})
      : super(
          message: message,
          messageHi: 'इस विवरण के साथ एक रिकॉर्ड पहले से मौजूद है।',
          statusCode: 409,
          details: raw,
        );
}

class ValidationException extends ApiException {
  ValidationException(String message, {dynamic raw})
      : super(
          message: message,
          messageHi: 'कृपया दर्ज की गई जानकारी की जांच करें।',
          statusCode: 422,
          details: raw,
        );
}

class BadRequestException extends ApiException {
  BadRequestException(String message, {dynamic raw})
      : super(
          message: message,
          messageHi: 'अमान्य अनुरोध विवरण।',
          statusCode: 400,
          details: raw,
        );
}

class RateLimitException extends ApiException {
  RateLimitException(String message, {dynamic raw})
      : super(
          message: message,
          messageHi: 'बहुत अधिक अनुरोध। कृपया कुछ समय बाद पुनः प्रयास करें।',
          statusCode: 429,
          details: raw,
        );
}

class ServerException extends ApiException {
  ServerException(String message, {dynamic raw})
      : super(
          message: message,
          messageHi: 'जनसेतु सर्वर पर समस्या आई है। कृपया बाद में प्रयास करें।',
          statusCode: 500,
          details: raw,
        );
}

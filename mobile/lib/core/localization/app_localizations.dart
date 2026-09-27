import 'package:flutter/material.dart';

class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations) ??
        AppLocalizations(const Locale('hi'));
  }

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  bool get isHindi => locale.languageCode == 'hi';
  String get currentLanguageCode => locale.languageCode;

  // Bilingual Dictionary matching frontend/src/i18n/en.json and hi.json
  static final Map<String, Map<String, String>> _localizedValues = {
    'en': {
      // Common
      'common.loading': 'Loading...',
      'common.error': 'An error occurred',
      'common.retry': 'Retry',
      'common.save': 'Save Changes',
      'common.cancel': 'Cancel',
      'common.back': 'Back',
      'common.next': 'Continue',
      'common.success': 'Success',
      'common.close': 'Close',
      'common.officialHandoff': 'Official Government Portal Handoff',
      'common.verified': 'Verified',
      'common.pending': 'Pending',
      'common.needsReview': 'Action Required',
      'common.offline': "You're offline. Reconnecting to JanSetu...",
      'common.serverError': 'JanSetu could not reach the server.',

      // Nav
      'nav.home': 'Home',
      'nav.benefits': 'Benefits',
      'nav.documents': 'Documents',
      'nav.applications': 'Applications',
      'nav.profile': 'Profile',
      'nav.survival': 'Survival Map',
      'nav.agent': 'AI Assistant',
      'nav.logout': 'Log Out',

      // Auth
      'auth.login': 'Log In',
      'auth.register': 'Create Account',
      'auth.welcomeBack': 'Welcome to JanSetu',
      'auth.tagline': 'The Sovereign Citizen Welfare Bridge of India',
      'auth.loginDesc': 'Securely access your entitled state & central benefits with verifiable cryptographic identity.',
      'auth.registerDesc': 'Register in 30 seconds to discover, protect, and claim every welfare scheme you qualify for.',
      'auth.emailLabel': 'Email Address',
      'auth.emailPlaceholder': 'citizen@example.gov.in',
      'auth.phoneLabel': 'Mobile Number',
      'auth.phonePlaceholder': '9876543210',
      'auth.passwordLabel': 'Password',
      'auth.passwordPlaceholder': 'Minimum 8 characters',
      'auth.confirmPasswordLabel': 'Confirm Password',
      'auth.confirmPasswordPlaceholder': 'Re-enter your password',
      'auth.forgotPassword': 'Forgot password?',
      'auth.noAccount': "Don't have an account?",
      'auth.haveAccount': 'Already registered?',
      'auth.loginBtn': 'Access Welfare Portal',
      'auth.registerBtn': 'Create Citizen Account',
      'auth.authenticating': 'Verifying Credentials...',
      'auth.creatingAccount': 'Establishing Citizen Record...',
      'auth.errorMismatch': 'Passwords do not match',
      'auth.errorShortPass': 'Password must be at least 8 characters',
      'auth.errorRequired': 'Please fill in all mandatory fields',
      'auth.termsConsent': "By proceeding, you agree to JanSetu's Citizen Data Protection & Sovereign Privacy charter.",

      // Onboarding
      'onboarding.badge': 'Citizen Profile Setup',
      'onboarding.title': 'Build Your Welfare Identity',
      'onboarding.subtitle': 'Provide your household and occupation details once. JanSetu continuously matches you with every central and state welfare scheme without repetitive paperwork.',
      'onboarding.step1': 'Personal',
      'onboarding.step2': 'Location',
      'onboarding.step3': 'Employment',
      'onboarding.step4': 'Household',
      'onboarding.name': 'Full Legal Name',
      'onboarding.nameHint': 'As per Aadhaar or Voter ID',
      'onboarding.dob': 'Date of Birth',
      'onboarding.gender': 'Gender',
      'onboarding.genderMale': 'Male',
      'onboarding.genderFemale': 'Female',
      'onboarding.genderOther': 'Other',
      'onboarding.caste': 'Social Category',
      'onboarding.casteGeneral': 'General',
      'onboarding.casteOBC': 'OBC',
      'onboarding.casteSC': 'SC',
      'onboarding.casteST': 'ST',
      'onboarding.currentState': 'Current State',
      'onboarding.currentDistrict': 'Current District',
      'onboarding.permanentState': 'Permanent State',
      'onboarding.permanentDistrict': 'Permanent District',
      'onboarding.isMigrant': 'Are you currently working or residing away from your home state?',
      'onboarding.migrantYes': 'Yes, Migrant Worker / Inter-State',
      'onboarding.migrantNo': 'No, Resident in Home District',
      'onboarding.occupation': 'Primary Occupation',
      'onboarding.occupationSector': 'Employment Sector',
      'onboarding.monthlyIncome': 'Monthly Household Income (INR)',
      'onboarding.hasDisability': 'Person with Disability (PwD)?',
      'onboarding.saving': 'Saving Citizen Profile...',
      'onboarding.complete': 'Complete Setup & Unlock Benefits',

      // Dashboard
      'dashboard.sovereignBadge': 'Sovereign Welfare Status',
      'dashboard.welcome': 'Welcome',
      'dashboard.activeSchemes': 'Available Benefits',
      'dashboard.protectedMonthly': 'Direct Monthly Entitlement',
      'dashboard.readinessScore': 'Evidence Readiness',
      'dashboard.actionNeeded': 'Actions Needed',
      'dashboard.recentApplications': 'Application Pipelines',
      'dashboard.exploreAll': 'View All Benefits',

      // Benefits
      'benefits.title': 'Discovered Welfare Benefits',
      'benefits.subtitle': 'Verified entitlements computed strictly from official government criteria and your authenticated citizen profile.',
      'benefits.whyApply': 'Why This May Apply to You',
      'benefits.matchedRules': 'Matched Statutory Criteria',
      'benefits.unmetRules': 'Pending / Unmet Requirements',
      'benefits.requiredDocs': 'Required Evidence Documents',
      'benefits.applyNow': 'Prepare Sovereign Application',
      'benefits.viewDetail': 'View Criteria & Evidence',

      // Documents
      'documents.title': 'Sovereign Evidence Vault',
      'documents.subtitle': 'Cryptographically verified documents supporting your welfare rights. Zero fake uploads; tamper-evident storage.',
      'documents.uploadBtn': 'Upload Government Document',
      'documents.cameraBtn': 'Scan / Take Photo',
      'documents.uploading': 'Uploading to Sovereign Vault...',
      'documents.processing': 'Extracting Official Evidence...',
      'documents.ready': 'Verified & Ready',
      'documents.noDocs': 'No documents uploaded yet. Add an ID or income certificate to unlock benefits.',

      // Applications
      'applications.title': 'Welfare Applications',
      'applications.subtitle': 'Transparent tracking of all prepared, reviewed, and officially handed off government submissions.',
      'applications.pipelinePrepared': 'Prepared',
      'applications.pipelineReviewed': 'Reviewed',
      'applications.pipelineConsent': 'Consent Granted',
      'applications.pipelineHandoff': 'Official Handoff / Submitted',
      'applications.pipelineGovReview': 'Government Processing',
      'applications.pipelineApproved': 'Approved / Granted',

      // Consent
      'consent.modalTitle': 'Sovereign Citizen Consent',
      'consent.readyToContinue': 'Ready to continue?',
      'consent.youAreInControl': 'You are in sovereign control of your data.',
      'consent.grant': 'Give Consent & Continue',
      'consent.reviewAgain': 'Review Again',
      'consent.processing': 'Recording Cryptographic Consent...',

      // Agent
      'agent.title': 'JanSetu Sovereign Assistant',
      'agent.subtitle': 'Deterministic welfare policy guidance powered by Google Gemini and official gazettes.',
      'agent.inputHint': 'Ask about schemes, missing documents, or eligibility in Hindi or English...',
      'agent.voiceListening': 'Listening to citizen...',
      'agent.voicePrompt': 'Speak now (Hindi / English)',
    },
    'hi': {
      // Common
      'common.loading': 'लोड हो रहा है...',
      'common.error': 'एक त्रुटि हुई',
      'common.retry': 'पुनः प्रयास करें',
      'common.save': 'बदलाव सुरक्षित करें',
      'common.cancel': 'रद्द करें',
      'common.back': 'पीछे जाएं',
      'common.next': 'आगे बढ़ें',
      'common.success': 'सफल',
      'common.close': 'बंद करें',
      'common.officialHandoff': 'आधिकारिक सरकारी पोर्टल हैंडऑफ',
      'common.verified': 'सत्यापित',
      'common.pending': 'प्रक्रियाधीन',
      'common.needsReview': 'कार्रवाई आवश्यक',
      'common.offline': 'आप ऑफलाइन हैं। जनसेतु से पुनः संपर्क किया जा रहा है...',
      'common.serverError': 'जनसेतु सर्वर से संपर्क नहीं हो सका।',

      // Nav
      'nav.home': 'होम',
      'nav.benefits': 'योजनाएं',
      'nav.documents': 'दस्तावेज़',
      'nav.applications': 'आवेदन',
      'nav.profile': 'प्रोफ़ाइल',
      'nav.survival': 'सुरक्षा नक्शा',
      'nav.agent': 'AI सहायक',
      'nav.logout': 'लॉग आउट',

      // Auth
      'auth.login': 'लॉगिन करें',
      'auth.register': 'खाता बनाएं',
      'auth.welcomeBack': 'जनसेतु में आपका स्वागत है',
      'auth.tagline': 'भारत का संप्रभु नागरिक कल्याण सेतु',
      'auth.loginDesc': 'सत्यापन योग्य पहचान के साथ अपने सभी हकदार केंद्रीय एवं राज्य कल्याणकारी लाभों तक पहुंचें।',
      'auth.registerDesc': '30 सेकंड में पंजीकरण करें और हर उस सरकारी योजना को खोजें व सुरक्षित करें जिसके आप पात्र हैं।',
      'auth.emailLabel': 'ईमेल पता',
      'auth.emailPlaceholder': 'citizen@example.gov.in',
      'auth.phoneLabel': 'मोबाइल नंबर',
      'auth.phonePlaceholder': '9876543210',
      'auth.passwordLabel': 'पासवर्ड',
      'auth.passwordPlaceholder': 'कम से कम 8 अक्षर',
      'auth.confirmPasswordLabel': 'पासवर्ड की पुष्टि करें',
      'auth.confirmPasswordPlaceholder': 'अपना पासवर्ड पुनः दर्ज करें',
      'auth.forgotPassword': 'पासवर्ड भूल गए?',
      'auth.noAccount': 'क्या आपका खाता नहीं है?',
      'auth.haveAccount': 'पहले से पंजीकृत हैं?',
      'auth.loginBtn': 'कल्याण पोर्टल में प्रवेश करें',
      'auth.registerBtn': 'नागरिक खाता बनाएं',
      'auth.authenticating': 'पहचान सत्यापित की जा रही है...',
      'auth.creatingAccount': 'नागरिक रिकॉर्ड तैयार किया जा रहा है...',
      'auth.errorMismatch': 'पासवर्ड मेल नहीं खा रहे हैं',
      'auth.errorShortPass': 'पासवर्ड कम से कम 8 अक्षरों का होना चाहिए',
      'auth.errorRequired': 'कृपया सभी अनिवार्य विवरण भरें',
      'auth.termsConsent': 'आगे बढ़ने पर आप जनसेतु नागरिक डेटा संरक्षण और संप्रभु गोपनीयता शर्तों से सहमत होते हैं।',

      // Onboarding
      'onboarding.badge': 'नागरिक प्रोफ़ाइल सेटअप',
      'onboarding.title': 'अपनी कल्याणकारी पहचान बनाएं',
      'onboarding.subtitle': 'अपने परिवार और व्यवसाय का विवरण केवल एक बार दर्ज करें। जनसेतु बिना किसी कागज़ी झंझट के आपको हर केंद्रीय और राज्य योजना से जोड़ता है।',
      'onboarding.step1': 'व्यक्तिगत',
      'onboarding.step2': 'स्थान',
      'onboarding.step3': 'रोज़गार',
      'onboarding.step4': 'परिवार',
      'onboarding.name': 'पूरा कानूनी नाम',
      'onboarding.nameHint': 'आधार या मतदाता पहचान पत्र के अनुसार',
      'onboarding.dob': 'जन्म तिथि',
      'onboarding.gender': 'लिंग',
      'onboarding.genderMale': 'पुरुष',
      'onboarding.genderFemale': 'महिला',
      'onboarding.genderOther': 'अन्य',
      'onboarding.caste': 'सामाजिक श्रेणी (जाति)',
      'onboarding.casteGeneral': 'सामान्य',
      'onboarding.casteOBC': 'अन्य पिछड़ा वर्ग (OBC)',
      'onboarding.casteSC': 'अनुसूचित जाति (SC)',
      'onboarding.casteST': 'अनुसूचित जनजाति (ST)',
      'onboarding.currentState': 'वर्तमान राज्य',
      'onboarding.currentDistrict': 'वर्तमान जिला',
      'onboarding.permanentState': 'मूल (स्थाई) राज्य',
      'onboarding.permanentDistrict': 'मूल जिला',
      'onboarding.isMigrant': 'क्या आप अपने गृह राज्य से बाहर काम या निवास कर रहे हैं?',
      'onboarding.migrantYes': 'हाँ, प्रवासी श्रमिक / अंतर-राज्यीय',
      'onboarding.migrantNo': 'नहीं, गृह जिले में ही निवासी',
      'onboarding.occupation': 'मुख्य व्यवसाय',
      'onboarding.occupationSector': 'कार्य क्षेत्र',
      'onboarding.monthlyIncome': 'मासिक पारिवारिक आय (₹)',
      'onboarding.hasDisability': 'क्या दिव्यांगजन (PwD) हैं?',
      'onboarding.saving': 'नागरिक प्रोफ़ाइल सुरक्षित की जा रही है...',
      'onboarding.complete': 'सेटअप पूरा करें एवं योजनाओं को अनलॉक करें',

      // Dashboard
      'dashboard.sovereignBadge': 'संप्रभु कल्याण स्थिति',
      'dashboard.welcome': 'स्वागत है',
      'dashboard.activeSchemes': 'पात्र सरकारी योजनाएं',
      'dashboard.protectedMonthly': 'मासिक प्रत्यक्ष हकदारी',
      'dashboard.readinessScore': 'दस्तावेज़ पूर्णता स्कोर',
      'dashboard.actionNeeded': 'आवश्यक कार्रवाइयां',
      'dashboard.recentApplications': 'आवेदन पाइपलाइन',
      'dashboard.exploreAll': 'सभी योजनाएं देखें',

      // Benefits
      'benefits.title': 'खोजे गए कल्याणकारी लाभ',
      'benefits.subtitle': 'सरकारी राजपत्रों और आपकी सत्यापित प्रोफ़ाइल के आधार पर सीधे निर्धारित लाभ।',
      'benefits.whyApply': 'यह योजना आपके लिए क्यों लागू हो सकती है',
      'benefits.matchedRules': 'संतुष्ट वैधानिक शर्तें',
      'benefits.unmetRules': 'लंबित / असंतुष्ट आवश्यकताएं',
      'benefits.requiredDocs': 'आवश्यक प्रमाण दस्तावेज़',
      'benefits.applyNow': 'संप्रभु आवेदन तैयार करें',
      'benefits.viewDetail': 'शर्तें व प्रमाण देखें',

      // Documents
      'documents.title': 'संप्रभु दस्तावेज़ भंडार',
      'documents.subtitle': 'आपके कल्याणकारी अधिकारों को प्रमाणित करने वाले सुरक्षित दस्तावेज़। कोई फर्जी अपलोड नहीं।',
      'documents.uploadBtn': 'सरकारी दस्तावेज़ अपलोड करें',
      'documents.cameraBtn': 'कैमरा से स्कैन करें',
      'documents.uploading': 'सुरक्षित भंडार में अपलोड हो रहा है...',
      'documents.processing': 'सरकारी प्रमाण निकाला जा रहा है...',
      'documents.ready': 'सत्यापित एवं तैयार',
      'documents.noDocs': 'अभी कोई दस्तावेज़ अपलोड नहीं है। लाभ पाने के लिए पहचान या आय प्रमाण पत्र जोड़ें।',

      // Applications
      'applications.title': 'कल्याणकारी आवेदन',
      'applications.subtitle': 'तैयार, समीक्षित एवं आधिकारिक रूप से प्रस्तुत सरकारी आवेदनों की पारदर्शी स्थिति।',
      'applications.pipelinePrepared': 'तैयार किया गया',
      'applications.pipelineReviewed': 'समीक्षित',
      'applications.pipelineConsent': 'सहमति स्वीकृत',
      'applications.pipelineHandoff': 'आधिकारिक हैंडऑफ / प्रस्तुत',
      'applications.pipelineGovReview': 'सरकारी समीक्षा में',
      'applications.pipelineApproved': 'स्वीकृत / प्रदान किया गया',

      // Consent
      'consent.modalTitle': 'संप्रभु नागरिक सहमति',
      'consent.readyToContinue': 'क्या आप आगे बढ़ना चाहते हैं?',
      'consent.youAreInControl': 'आप अपने व्यक्तिगत डेटा के पूर्ण स्वामी हैं।',
      'consent.grant': 'सहमति दें और आगे बढ़ें',
      'consent.reviewAgain': 'पुनः समीक्षा करें',
      'consent.processing': 'सहमति दर्ज की जा रही है...',

      // Agent
      'agent.title': 'जनसेतु संप्रभु सहायक',
      'agent.subtitle': 'गूगल जेमिनी और आधिकारिक राजपत्रों द्वारा संचालित विश्वसनीय मार्गदर्शन।',
      'agent.inputHint': 'योजनाओं, आवश्यक दस्तावेज़ों या पात्रता के बारे में हिंदी या अंग्रेज़ी में पूछें...',
      'agent.voiceListening': 'नागरिक की बात सुनी जा रही है...',
      'agent.voicePrompt': 'अब बोलें (हिंदी / अंग्रेज़ी)',
    },
  };

  String text(String key) {
    final lang = locale.languageCode == 'hi' ? 'hi' : 'en';
    final val = _localizedValues[lang]?[key];
    if (val != null) return val;
    // Fallback to English if missing in Hindi
    return _localizedValues['en']?[key] ?? key;
  }
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => ['en', 'hi'].contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

extension AppLocalizationsExtension on BuildContext {
  AppLocalizations get l10n => AppLocalizations.of(this);
}

import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../core/localization/app_localizations.dart';
import '../core/models/models.dart';
import '../core/repositories/citizen_repository.dart';
import '../core/theme/tokens.dart';
import '../shared/widgets/cinematic_scaffold.dart';
import '../shared/widgets/glass_card.dart';
import '../shared/widgets/gold_button.dart';

class DocumentsScreen extends StatefulWidget {
  final CitizenRepository citizenRepository;

  const DocumentsScreen({super.key, required this.citizenRepository});

  @override
  State<DocumentsScreen> createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> {
  bool _isLoading = true;
  bool _isUploading = false;
  String? _errorMessage;
  List<DocumentItemModel> _documents = [];
  final ImagePicker _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _fetchDocuments();
  }

  Future<void> _fetchDocuments() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final docs = await widget.citizenRepository.getDocuments();
      if (mounted) {
        setState(() {
          _documents = docs;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().replaceAll('ApiException: ', '');
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _pickAndUploadDocument({required bool fromCamera}) async {
    final l10n = context.l10n;

    try {
      List<int>? fileBytes;
      String? fileName;
      String docType = 'IDENTITY';
      String title = 'Citizen Document';

      if (fromCamera) {
        final photo = await _imagePicker.pickImage(source: ImageSource.camera, imageQuality: 85);
        if (photo == null) return;
        fileBytes = await photo.readAsBytes();
        fileName = photo.name;
        title = 'Identity Document (Camera Capture)';
      } else {
        final result = await FilePicker.platform.pickFiles(
          type: FileType.custom,
          allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png'],
          withData: true,
        );
        if (result == null || result.files.isEmpty) return;
        final file = result.files.first;
        fileBytes = file.bytes;
        if (fileBytes == null && file.path != null) {
          fileBytes = await File(file.path!).readAsBytes();
        }
        fileName = file.name;
        title = file.name;
        if (fileName.toLowerCase().contains('income')) {
          docType = 'INCOME_CERTIFICATE';
        } else if (fileName.toLowerCase().contains('caste')) {
          docType = 'CASTE_CERTIFICATE';
        } else if (fileName.toLowerCase().contains('ration')) {
          docType = 'RATION_CARD';
        }
      }

      if (fileBytes == null || fileBytes.isEmpty) return;

      setState(() {
        _isUploading = true;
        _errorMessage = null;
      });

      await widget.citizenRepository.uploadDocument(
        title: title,
        documentType: docType,
        fileBytes: fileBytes,
        fileName: fileName ?? 'document.pdf',
      );

      // Refresh list from real server
      await _fetchDocuments();
    } catch (e) {
      setState(() {
        _errorMessage = 'Upload failed: ${e.toString().replaceAll('ApiException: ', '')}';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isUploading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return CinematicScaffold(
      body: RefreshIndicator(
        onRefresh: _fetchDocuments,
        color: JanSetuTokens.goldPrimary,
        backgroundColor: JanSetuTokens.bgSurface,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              Text(
                l10n.text('documents.title'),
                style: const TextStyle(
                  color: JanSetuTokens.textPrimary,
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.3,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                l10n.text('documents.subtitle'),
                style: const TextStyle(
                  color: JanSetuTokens.textSecondary,
                  fontSize: 13,
                  height: 1.45,
                ),
              ),
              const SizedBox(height: 20),

              // Upload Buttons
              Row(
                children: [
                  Expanded(
                    child: GoldButton(
                      text: 'Upload File / PDF',
                      icon: Icons.upload_file_rounded,
                      isLoading: _isUploading,
                      onPressed: () => _pickAndUploadDocument(fromCamera: false),
                      height: 48,
                    ),
                  ),
                  const SizedBox(width: 12),
                  IconButton.filled(
                    style: IconButton.styleFrom(
                      backgroundColor: JanSetuTokens.bgGlassSecondary,
                      padding: const EdgeInsets.all(14),
                    ),
                    icon: const Icon(Icons.camera_alt_outlined, color: JanSetuTokens.goldPrimary, size: 22),
                    onPressed: _isUploading ? null : () => _pickAndUploadDocument(fromCamera: true),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Uploading indicator
              if (_isUploading) ...[
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: JanSetuTokens.goldPrimary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: JanSetuTokens.goldPrimary.withOpacity(0.3)),
                  ),
                  child: Row(
                    children: [
                      const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(JanSetuTokens.goldPrimary),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          l10n.text('documents.uploading'),
                          style: const TextStyle(color: JanSetuTokens.goldPrimary, fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Error banner
              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: JanSetuTokens.rosePrimary.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: JanSetuTokens.rosePrimary.withOpacity(0.4)),
                  ),
                  child: Text(
                    _errorMessage!,
                    style: const TextStyle(color: JanSetuTokens.rosePrimary, fontSize: 13),
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Document List
              if (_isLoading) ...[
                const SizedBox(height: 60),
                const Center(
                  child: CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(JanSetuTokens.goldPrimary),
                  ),
                ),
              ] else if (_documents.isEmpty) ...[
                GlassCard(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    children: [
                      const Icon(Icons.folder_open_rounded, color: JanSetuTokens.goldPrimary, size: 48),
                      const SizedBox(height: 16),
                      Text(
                        l10n.text('documents.noDocs'),
                        style: const TextStyle(color: JanSetuTokens.textSecondary, fontSize: 14),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ] else ...[
                for (final doc in _documents) ...[
                  Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    child: GlassCard(
                      padding: const EdgeInsets.all(18),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(10),
                                decoration: BoxDecoration(
                                  color: JanSetuTokens.skyPrimary.withOpacity(0.12),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: const Icon(Icons.description_outlined, color: JanSetuTokens.skyPrimary, size: 22),
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      doc.title,
                                      style: const TextStyle(
                                        color: JanSetuTokens.textPrimary,
                                        fontSize: 15,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      '${doc.documentType} • ${(doc.fileSizeBytes / 1024).toStringAsFixed(1)} KB',
                                      style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 12),
                                    ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: doc.verificationStatus == 'verified'
                                      ? JanSetuTokens.emeraldPrimary.withOpacity(0.15)
                                      : JanSetuTokens.amberPrimary.withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  doc.verificationStatus.toUpperCase(),
                                  style: TextStyle(
                                    color: doc.verificationStatus == 'verified'
                                        ? JanSetuTokens.emeraldPrimary
                                        : JanSetuTokens.amberPrimary,
                                    fontSize: 10,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          if (doc.extractedFields != null && doc.extractedFields!.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            const Divider(color: JanSetuTokens.glassBorderSubtle, height: 1),
                            const SizedBox(height: 10),
                            const Text(
                              'Verified Extracted Evidence:',
                              style: TextStyle(color: JanSetuTokens.goldPrimary, fontSize: 12, fontWeight: FontWeight.w600),
                            ),
                            const SizedBox(height: 6),
                            for (final entry in doc.extractedFields!.entries.take(3)) ...[
                              Padding(
                                padding: const EdgeInsets.symmetric(vertical: 2),
                                child: Row(
                                  children: [
                                    Text(
                                      '${entry.key}: ',
                                      style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 12),
                                    ),
                                    Text(
                                      '${entry.value}',
                                      style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 12, fontWeight: FontWeight.w500),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ],
                        ],
                      ),
                    ),
                  ),
                ],
              ],
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

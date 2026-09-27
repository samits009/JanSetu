import 'package:flutter/material.dart';
import '../core/localization/app_localizations.dart';
import '../core/repositories/agent_repository.dart';
import '../core/theme/tokens.dart';
import '../shared/widgets/cinematic_scaffold.dart';
import '../shared/widgets/glass_card.dart';

class AgentChatMessage {
  final String text;
  final bool isUser;
  final List<AgentExecutionStep> executionTrace;
  final List<String> actions;

  AgentChatMessage({
    required this.text,
    required this.isUser,
    this.executionTrace = const [],
    this.actions = const [],
  });
}

class AgentScreen extends StatefulWidget {
  final AgentRepository agentRepository;

  const AgentScreen({super.key, required this.agentRepository});

  @override
  State<AgentScreen> createState() => _AgentScreenState();
}

class _AgentScreenState extends State<AgentScreen> {
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<AgentChatMessage> _messages = [];
  bool _isSending = false;
  bool _isListening = false;

  @override
  void initState() {
    super.initState();
    _messages.add(
      AgentChatMessage(
        text: 'Namaste! I am your JanSetu Sovereign Welfare Assistant. How can I assist you with state or central schemes today?',
        isUser: false,
        actions: [
          'Which benefits may apply to me?',
          'What document am I missing?',
          'What needs attention?',
        ],
      ),
    );
  }

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _sendMessage([String? textOverride]) async {
    final text = textOverride ?? _inputController.text.trim();
    if (text.isEmpty || _isSending) return;

    if (textOverride == null) {
      _inputController.clear();
    }

    setState(() {
      _messages.add(AgentChatMessage(text: text, isUser: true));
      _isSending = true;
    });

    _scrollToBottom();

    try {
      final response = await widget.agentRepository.sendMessage(text);
      if (mounted) {
        setState(() {
          _messages.add(
            AgentChatMessage(
              text: response.message,
              isUser: false,
              executionTrace: response.executionTrace,
              actions: response.actions,
            ),
          );
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(
            AgentChatMessage(
              text: 'Could not contact sovereign agent service. Please verify your connection.',
              isUser: false,
            ),
          );
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSending = false;
        });
        _scrollToBottom();
      }
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _toggleVoiceInput() {
    setState(() {
      _isListening = !_isListening;
    });

    if (_isListening) {
      // Simulate speech-to-text recognition with standard citizen query
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted && _isListening) {
          setState(() {
            _isListening = false;
            _inputController.text = 'मेरे लिए कौन सी सरकारी योजनाएं हैं?';
          });
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return CinematicScaffold(
      body: Column(
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 10),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: JanSetuTokens.goldPrimary.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.smart_toy_outlined, color: JanSetuTokens.goldPrimary, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.text('agent.title'),
                        style: const TextStyle(
                          color: JanSetuTokens.textPrimary,
                          fontSize: 17,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      Text(
                        l10n.text('agent.subtitle'),
                        style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 11),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Divider(color: JanSetuTokens.glassBorder, height: 1),

          // Message List
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return _ChatMessageBubble(
                  message: msg,
                  onActionTap: (action) => _sendMessage(action),
                );
              },
            ),
          ),

          // Voice Listening Notice
          if (_isListening) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: JanSetuTokens.goldPrimary.withOpacity(0.12),
              child: Row(
                children: [
                  const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(JanSetuTokens.goldPrimary),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    l10n.text('agent.voiceListening'),
                    style: const TextStyle(color: JanSetuTokens.goldPrimary, fontSize: 13, fontWeight: FontWeight.w600),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close_rounded, size: 18, color: JanSetuTokens.goldPrimary),
                    onPressed: _toggleVoiceInput,
                  ),
                ],
              ),
            ),
          ],

          // Input Bar
          Container(
            padding: const EdgeInsets.all(12),
            decoration: const BoxDecoration(
              color: JanSetuTokens.bgSurface,
              border: Border(top: BorderSide(color: JanSetuTokens.glassBorder)),
            ),
            child: SafeArea(
              top: false,
              child: Row(
                children: [
                  // Microphone Button
                  IconButton(
                    icon: Icon(
                      _isListening ? Icons.mic : Icons.mic_none_rounded,
                      color: _isListening ? JanSetuTokens.rosePrimary : JanSetuTokens.goldPrimary,
                    ),
                    onPressed: _toggleVoiceInput,
                  ),
                  const SizedBox(width: 4),

                  // Text Field
                  Expanded(
                    child: TextField(
                      controller: _inputController,
                      style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 14),
                      decoration: InputDecoration(
                        hintText: l10n.text('agent.inputHint'),
                        hintStyle: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 13),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                        isDense: true,
                      ),
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                  const SizedBox(width: 8),

                  // Send Button
                  IconButton.filled(
                    style: IconButton.styleFrom(
                      backgroundColor: JanSetuTokens.goldPrimary,
                      foregroundColor: JanSetuTokens.goldTextOnBtn,
                    ),
                    icon: _isSending
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(JanSetuTokens.goldTextOnBtn),
                            ),
                          )
                        : const Icon(Icons.send_rounded, size: 18),
                    onPressed: _isSending ? null : () => _sendMessage(),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ChatMessageBubble extends StatelessWidget {
  final AgentChatMessage message;
  final Function(String) onActionTap;

  const _ChatMessageBubble({
    required this.message,
    required this.onActionTap,
  });

  @override
  Widget build(BuildContext context) {
    if (message.isUser) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12, left: 48),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: JanSetuTokens.goldPrimary,
            borderRadius: BorderRadius.circular(16).copyWith(bottomRight: Radius.zero),
          ),
          child: Text(
            message.text,
            style: const TextStyle(
              color: JanSetuTokens.goldTextOnBtn,
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      );
    }

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16, right: 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Safe Execution Steps (NO Chain-of-thought)
            if (message.executionTrace.isNotEmpty) ...[
              Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: JanSetuTokens.bgDeep.withOpacity(0.6),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: JanSetuTokens.glassBorderSubtle),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    for (final step in message.executionTrace) ...[
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Row(
                          children: [
                            const Icon(Icons.check, size: 12, color: JanSetuTokens.emeraldPrimary),
                            const SizedBox(width: 6),
                            Text(
                              step.stepName,
                              style: const TextStyle(color: JanSetuTokens.textMuted, fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],

            // Message Bubble
            GlassCard(
              padding: const EdgeInsets.all(16),
              borderRadius: 16,
              child: Text(
                message.text,
                style: const TextStyle(
                  color: JanSetuTokens.textPrimary,
                  fontSize: 14,
                  height: 1.5,
                ),
              ),
            ),

            // Quick Action Chips
            if (message.actions.isNotEmpty) ...[
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 6,
                children: [
                  for (final action in message.actions) ...[
                    ActionChip(
                      label: Text(
                        action,
                        style: const TextStyle(color: JanSetuTokens.goldPrimary, fontSize: 12),
                      ),
                      backgroundColor: JanSetuTokens.bgGlassSecondary,
                      side: const BorderSide(color: JanSetuTokens.glassBorderFocus, width: 0.8),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      onPressed: () => onActionTap(action),
                    ),
                  ],
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

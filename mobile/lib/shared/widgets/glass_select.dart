import 'dart:ui';
import 'package:flutter/material.dart';
import '../../core/theme/tokens.dart';

class GlassSelectOption {
  final String value;
  final String label;
  final String? group;

  const GlassSelectOption({
    required this.value,
    required this.label,
    this.group,
  });
}

class GlassSelect extends StatefulWidget {
  final String? value;
  final String placeholder;
  final String label;
  final List<GlassSelectOption> options;
  final ValueChanged<String?> onChanged;
  final bool enabled;
  final IconData? prefixIcon;

  const GlassSelect({
    super.key,
    required this.value,
    required this.placeholder,
    required this.label,
    required this.options,
    required this.onChanged,
    this.enabled = true,
    this.prefixIcon,
  });

  @override
  State<GlassSelect> createState() => _GlassSelectState();
}

class _GlassSelectState extends State<GlassSelect> with SingleTickerProviderStateMixin {
  late AnimationController _chevronController;

  @override
  void initState() {
    super.initState();
    _chevronController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 200),
    );
  }

  @override
  void dispose() {
    _chevronController.dispose();
    super.dispose();
  }

  void _openSelectionSheet() async {
    if (!widget.enabled) return;

    _chevronController.forward();

    final result = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _GlassSelectModal(
        label: widget.label,
        options: widget.options,
        initialValue: widget.value,
      ),
    );

    _chevronController.reverse();

    if (result != null && result != widget.value) {
      widget.onChanged(result);
    }
  }

  @override
  Widget build(BuildContext context) {
    final selectedOption = widget.options.cast<GlassSelectOption?>().firstWhere(
          (o) => o?.value == widget.value,
          orElse: () => null,
        );

    final displayLabel = selectedOption?.label ?? widget.placeholder;
    final isSelected = selectedOption != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.label,
          style: const TextStyle(
            color: JanSetuTokens.textSecondary,
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 6),
        InkWell(
          onTap: widget.enabled ? _openSelectionSheet : null,
          borderRadius: BorderRadius.circular(14),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(14),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
              child: Container(
                height: 52, // 44px+ touch target
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: widget.enabled
                      ? JanSetuTokens.bgGlassSecondary
                      : JanSetuTokens.bgGlassSecondary.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: isSelected
                        ? JanSetuTokens.glassBorderFocus.withOpacity(0.5)
                        : JanSetuTokens.glassBorder,
                  ),
                ),
                child: Row(
                  children: [
                    if (widget.prefixIcon != null) ...[
                      Icon(
                        widget.prefixIcon,
                        size: 18,
                        color: isSelected
                            ? JanSetuTokens.goldPrimary
                            : JanSetuTokens.textMuted,
                      ),
                      const SizedBox(width: 12),
                    ],
                    Expanded(
                      child: Text(
                        displayLabel,
                        style: TextStyle(
                          color: isSelected
                              ? JanSetuTokens.textPrimary
                              : JanSetuTokens.textMuted,
                          fontSize: 15,
                          fontWeight: isSelected ? FontWeight.w500 : FontWeight.w400,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    RotationTransition(
                      turns: Tween(begin: 0.0, end: 0.5).animate(_chevronController),
                      child: const Icon(
                        Icons.keyboard_arrow_down_rounded,
                        color: JanSetuTokens.goldPrimary,
                        size: 20,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _GlassSelectModal extends StatefulWidget {
  final String label;
  final List<GlassSelectOption> options;
  final String? initialValue;

  const _GlassSelectModal({
    required this.label,
    required this.options,
    this.initialValue,
  });

  @override
  State<_GlassSelectModal> createState() => _GlassSelectModalState();
}

class _GlassSelectModalState extends State<_GlassSelectModal> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      setState(() {
        _searchQuery = _searchController.text.toLowerCase().trim();
      });
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final filtered = widget.options.where((opt) {
      if (_searchQuery.isEmpty) return true;
      return opt.label.toLowerCase().contains(_searchQuery) ||
          (opt.group?.toLowerCase().contains(_searchQuery) ?? false);
    }).toList();

    return ClipRRect(
      borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          height: MediaQuery.of(context).size.height * 0.75,
          decoration: BoxDecoration(
            color: JanSetuTokens.bgSurface.withOpacity(0.92),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
            border: const Border(
              top: BorderSide(color: JanSetuTokens.glassBorderFocus, width: 1.5),
              left: BorderSide(color: JanSetuTokens.glassBorder),
              right: BorderSide(color: JanSetuTokens.glassBorder),
            ),
          ),
          child: Column(
            children: [
              // Drag handle
              const SizedBox(height: 12),
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: JanSetuTokens.glassBorder,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: 16),

              // Title
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Row(
                  children: [
                    Text(
                      widget.label,
                      style: const TextStyle(
                        color: JanSetuTokens.textPrimary,
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close_rounded, color: JanSetuTokens.textMuted),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
              ),

              // Search input
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                child: TextField(
                  controller: _searchController,
                  style: const TextStyle(color: JanSetuTokens.textPrimary, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Search options...',
                    prefixIcon: const Icon(Icons.search_rounded, color: JanSetuTokens.goldPrimary, size: 20),
                    suffixIcon: _searchQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear_rounded, size: 18, color: JanSetuTokens.textMuted),
                            onPressed: () => _searchController.clear(),
                          )
                        : null,
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                  ),
                ),
              ),
              const Divider(color: JanSetuTokens.glassBorder, height: 1),

              // Option list
              Expanded(
                child: filtered.isEmpty
                    ? const Center(
                        child: Text(
                          'No matching items found',
                          style: TextStyle(color: JanSetuTokens.textMuted, fontSize: 14),
                        ),
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        itemCount: filtered.length,
                        separatorBuilder: (c, i) {
                          // If current and next have different groups, show header
                          return const Divider(color: JanSetuTokens.glassBorderSubtle, height: 1);
                        },
                        itemBuilder: (context, index) {
                          final item = filtered[index];
                          final isSelected = item.value == widget.initialValue;

                          // Show group header if first of its group
                          final prevGroup = index > 0 ? filtered[index - 1].group : null;
                          final showGroupHeader = item.group != null && item.group != prevGroup;

                          return Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              if (showGroupHeader)
                                Container(
                                  width: double.infinity,
                                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 4),
                                  color: Colors.white.withOpacity(0.02),
                                  child: Text(
                                    item.group!.toUpperCase(),
                                    style: const TextStyle(
                                      color: JanSetuTokens.goldPrimary,
                                      fontSize: 11,
                                      fontWeight: FontWeight.w700,
                                      letterSpacing: 1.0,
                                    ),
                                  ),
                                ),
                              InkWell(
                                onTap: () => Navigator.pop(context, item.value),
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                                  color: isSelected
                                      ? JanSetuTokens.goldPrimary.withOpacity(0.12)
                                      : Colors.transparent,
                                  child: Row(
                                    children: [
                                      Expanded(
                                        child: Text(
                                          item.label,
                                          style: TextStyle(
                                            color: isSelected
                                                ? JanSetuTokens.goldPrimary
                                                : JanSetuTokens.textPrimary,
                                            fontSize: 15,
                                            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                                          ),
                                        ),
                                      ),
                                      if (isSelected)
                                        const Icon(
                                          Icons.check_circle_rounded,
                                          color: JanSetuTokens.goldPrimary,
                                          size: 20,
                                        ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

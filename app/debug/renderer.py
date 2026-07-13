from app.debug.models import DebugInfo


class DebugRenderer:
    """
    Renders collected debug information into a human-readable format.
    """

    @staticmethod
    def render(debug_info: DebugInfo) -> str:
        lines = [
            "=" * 40,
            "Aether Debug Information",
            "=" * 40,
            "",
            f"Provider       : {debug_info.provider or 'Unknown'}",
            f"Model          : {debug_info.model or 'Unknown'}",
            f"Response Time  : "
            f"{debug_info.response_time_ms:.2f} ms"
            if debug_info.response_time_ms is not None
            else "Response Time  : N/A",
            f"Messages       : {debug_info.message_count}",
            f"Prompt Length  : {debug_info.prompt_length} characters",
            "",
            "Events:",
        ]

        if debug_info.events:
            for event in debug_info.events:
                lines.append(f"  • {event.name}")
        else:
            lines.append("  (No events recorded)")

        if debug_info.metadata:
            lines.extend(
                [
                    "",
                    "Metadata:",
                ]
            )

            for key, value in debug_info.metadata.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)
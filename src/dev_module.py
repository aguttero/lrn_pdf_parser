import logging

logger = logging.getLogger(__name__)


def extract_participant_list(response_data: dict) -> list[dict]:
    """Extract participant info from an Adobe Sign agreement API response.

    Iterates over ``participantSetsInfo`` and returns one dictionary per member
    in each set's ``memberInfos`` list, flattening role/order/label from the
    parent participant set onto each member.

    Args:
        response_data: Parsed JSON dict from the Adobe Sign agreement API
            (i.e. the result of ``api_response.json()``).

    Returns:
        A list of dicts, each with keys ``email``, ``name``, ``role``,
        ``order``, and ``label``. Returns an empty list when
        ``participantSetsInfo`` is missing or empty.

    Raises:
        ValueError: If any participant set has zero members in ``memberInfos``.
    """
    participant_sets = response_data.get("participantSetsInfo", [])
    result: list[dict] = []

    for pset in participant_sets:
        members = pset.get("memberInfos", [])

        if len(members) == 0:
            raise ValueError(f"participantSet '{pset.get('id', 'unknown')}' has no members")

        if len(members) > 1:
            logger.warning(
                f"participantSet '{pset.get('id', 'unknown')}' has {len(members)} members (expected 1)"
            )

        for member in members:
            result.append({
                "email": member.get("email", ""),
                "name": member.get("name", "").strip(),
                "role": pset.get("role", ""),
                "order": pset.get("order", ""),
                "label": pset.get("label", "").strip(),
            })

    return result
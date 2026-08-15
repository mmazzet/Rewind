from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import (
    EmailDeliveryError,
    NotAuthorisedError,
    TapeHasNoTracksError,
    TapeNotFoundError,
    TapeNotInDraftError,
    TapeNotReadyError,
    TapeNotSentError,
)
from app.models.tape import TapeStatus
from app.services import tape_service


@pytest.mark.asyncio
async def test_create_tape_success(mock_db):
    # Arrange: fake tape the repository will return
    mock_tape = MagicMock()
    mock_tape.id = 1
    mock_tape.title = "Summer Mix"
    mock_tape.cassette_style = "classic"
    mock_tape.length_minutes = 60
    mock_tape.sender_id = 42

    mock_repo_instance = MagicMock()
    mock_repo_instance.create = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        result = await tape_service.create_tape(
            db=mock_db,
            title="Summer Mix",
            cassette_style="classic",
            length_minutes=60,
            sender_id=42,
        )

    assert result.title == "Summer Mix"
    assert result.sender_id == 42


@pytest.mark.asyncio
async def test_get_tape_success(mock_db):
    mock_tape = MagicMock()
    mock_tape.id = 1
    mock_tape.sender_id = 42

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        result = await tape_service.get_tape(db=mock_db, tape_id=1, user_id=42)

    assert result.id == 1
    assert result.sender_id == 42


@pytest.mark.asyncio
async def test_get_tape_not_found(mock_db):
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=None)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotFoundError) as exc_info:
            await tape_service.get_tape(db=mock_db, tape_id=999, user_id=42)

    assert exc_info.value.message == "Tape not found"


@pytest.mark.asyncio
async def test_get_tape_wrong_user(mock_db):
    mock_tape = MagicMock()
    mock_tape.id = 1
    mock_tape.sender_id = 99  # different user

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(NotAuthorisedError) as exc_info:
            await tape_service.get_tape(db=mock_db, tape_id=1, user_id=42)

    assert exc_info.value.message == "Not authorised"


@pytest.mark.asyncio
async def test_mark_ready_not_found(mock_db):
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=None)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotFoundError):
            await tape_service.mark_ready(db=mock_db, tape_id=999, user_id=42)


@pytest.mark.asyncio
async def test_mark_ready_wrong_user(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 99  # different user

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(NotAuthorisedError):
            await tape_service.mark_ready(db=mock_db, tape_id=1, user_id=42)


@pytest.mark.asyncio
async def test_mark_ready_no_tracks(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = TapeStatus.draft
    mock_tape.tracks = []

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeHasNoTracksError):
            await tape_service.mark_ready(db=mock_db, tape_id=1, user_id=42)


@pytest.mark.asyncio
async def test_mark_ready_not_draft(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = TapeStatus.ready
    mock_tape.tracks = [MagicMock()]

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotInDraftError):
            await tape_service.mark_ready(db=mock_db, tape_id=1, user_id=42)


@pytest.mark.asyncio
async def test_mark_ready_success(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = TapeStatus.draft
    mock_tape.tracks = [MagicMock()]

    mock_updated_tape = MagicMock()
    mock_updated_tape.status = TapeStatus.ready

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)
    mock_repo_instance.update_status = AsyncMock(return_value=mock_updated_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        result = await tape_service.mark_ready(db=mock_db, tape_id=1, user_id=42)

    assert result.status == TapeStatus.ready
    mock_repo_instance.update_status.assert_called_once_with(
        mock_tape, TapeStatus.ready
    )


@pytest.mark.asyncio
async def test_send_tape_not_found(mock_db):
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=None)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotFoundError):
            await tape_service.send_tape(
                db=mock_db,
                tape_id=999,
                user_id=42,
                recipient_email="test@example.com",
                message=None,
            )


@pytest.mark.asyncio
async def test_send_tape_wrong_user(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 99

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(NotAuthorisedError):
            await tape_service.send_tape(
                db=mock_db,
                tape_id=1,
                user_id=42,
                recipient_email="test@example.com",
                message=None,
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [TapeStatus.draft, TapeStatus.sent],
)
async def test_send_tape_invalid_status(mock_db, status):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = status

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotReadyError):
            await tape_service.send_tape(
                db=mock_db,
                tape_id=1,
                user_id=42,
                recipient_email="test@example.com",
                message=None,
            )

    mock_repo_instance.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_send_tape_success(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = TapeStatus.ready

    mock_sent_tape = MagicMock()
    mock_sent_tape.status = TapeStatus.sent

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)
    mock_repo_instance.send_tape = AsyncMock(return_value=mock_sent_tape)

    with (
        patch(
            "app.services.tape_service.TapeRepository",
            return_value=mock_repo_instance,
        ),
        patch(
            "app.services.tape_service.email_service.send_tape_email",
            new_callable=AsyncMock,
        ) as mock_send_email,
        patch(
            "app.services.tape_service.user_repository.get_user_by_email",
            new=AsyncMock(return_value=None),
        ),
    ):
        result = await tape_service.send_tape(
            db=mock_db,
            tape_id=1,
            user_id=42,
            recipient_email="test@example.com",
            message="Made this for you",
        )

    assert result.status == TapeStatus.sent
    mock_repo_instance.send_tape.assert_awaited_once_with(
        tape=mock_tape,
        recipient_email="test@example.com",
        message="Made this for you",
        public_token=ANY,
    )
    mock_send_email.assert_awaited_once_with(
        recipient="test@example.com",
        public_token=ANY,
        message="Made this for you",
    )


@pytest.mark.asyncio
async def test_send_tape_email_failure_raises(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = TapeStatus.ready

    mock_sent_tape = MagicMock()
    mock_sent_tape.status = TapeStatus.sent

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)
    mock_repo_instance.send_tape = AsyncMock(return_value=mock_sent_tape)

    with (
        patch(
            "app.services.tape_service.TapeRepository",
            return_value=mock_repo_instance,
        ),
        patch(
            "app.services.tape_service.email_service.send_tape_email",
            new_callable=AsyncMock,
            side_effect=EmailDeliveryError("Could not send tape email"),
        ),
    ):
        with pytest.raises(EmailDeliveryError):
            await tape_service.send_tape(
                db=mock_db,
                tape_id=1,
                user_id=42,
                recipient_email="test@example.com",
                message="Made this for you",
            )


@pytest.mark.asyncio
async def test_get_public_tape_success(mock_db):
    mock_tape = MagicMock()
    mock_tape.status = TapeStatus.sent

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_public_token = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        result = await tape_service.get_public_tape(
            db=mock_db, public_token="some-token"
        )

    assert result.status == TapeStatus.sent


@pytest.mark.asyncio
async def test_get_public_tape_not_found(mock_db):
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_public_token = AsyncMock(return_value=None)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotFoundError):
            await tape_service.get_public_tape(db=mock_db, public_token="fake-token")


@pytest.mark.asyncio
async def test_get_public_tape_draft_not_accessible(mock_db):
    mock_tape = MagicMock()
    mock_tape.status = TapeStatus.draft

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_public_token = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotFoundError):
            await tape_service.get_public_tape(db=mock_db, public_token="some-token")


@pytest.mark.asyncio
async def test_archive_tape_not_found(mock_db):
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=None)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotFoundError):
            await tape_service.archive_tape(db=mock_db, tape_id=999, user_id=42)


@pytest.mark.asyncio
async def test_archive_tape_wrong_user(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 99

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(NotAuthorisedError):
            await tape_service.archive_tape(db=mock_db, tape_id=1, user_id=42)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [TapeStatus.draft, TapeStatus.ready, TapeStatus.archived],
)
async def test_archive_tape_not_sent(mock_db, status):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = status

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        with pytest.raises(TapeNotSentError):
            await tape_service.archive_tape(db=mock_db, tape_id=1, user_id=42)


@pytest.mark.asyncio
async def test_archive_tape_success(mock_db):
    mock_tape = MagicMock()
    mock_tape.sender_id = 42
    mock_tape.status = TapeStatus.sent

    mock_archived_tape = MagicMock()
    mock_archived_tape.status = TapeStatus.archived

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_id = AsyncMock(return_value=mock_tape)
    mock_repo_instance.update_status = AsyncMock(return_value=mock_archived_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        result = await tape_service.archive_tape(db=mock_db, tape_id=1, user_id=42)

    assert result.status == TapeStatus.archived
    mock_repo_instance.update_status.assert_called_once_with(
        mock_tape, TapeStatus.archived
    )


@pytest.mark.asyncio
async def test_claim_tapes_for_email_success(mock_db):
    mock_user = MagicMock()
    mock_user.id = 42
    mock_user.email = "maria@example.com"

    mock_tape = MagicMock()
    mock_tape.status = TapeStatus.sent

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_recipient_email = AsyncMock(return_value=[mock_tape])
    mock_repo_instance.update_status = AsyncMock(return_value=mock_tape)

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        await tape_service.claim_tapes_for_email(db=mock_db, user=mock_user)

    assert mock_tape.recipient_id == 42
    mock_repo_instance.update_status.assert_awaited_once_with(
        mock_tape, TapeStatus.claimed
    )


@pytest.mark.asyncio
async def test_claim_tapes_for_email_no_tapes(mock_db):
    mock_user = MagicMock()
    mock_user.id = 42
    mock_user.email = "maria@example.com"

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_recipient_email = AsyncMock(return_value=[])
    mock_repo_instance.update_status = AsyncMock()

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        await tape_service.claim_tapes_for_email(db=mock_db, user=mock_user)

    mock_repo_instance.update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_claim_tapes_for_email_multiple_tapes(mock_db):
    mock_user = MagicMock()
    mock_user.id = 42
    mock_user.email = "maria@example.com"

    mock_tape_1 = MagicMock()
    mock_tape_2 = MagicMock()

    mock_repo_instance = MagicMock()
    mock_repo_instance.get_by_recipient_email = AsyncMock(
        return_value=[mock_tape_1, mock_tape_2]
    )
    mock_repo_instance.update_status = AsyncMock()

    with patch(
        "app.services.tape_service.TapeRepository",
        return_value=mock_repo_instance,
    ):
        await tape_service.claim_tapes_for_email(db=mock_db, user=mock_user)

    assert mock_tape_1.recipient_id == 42
    assert mock_tape_2.recipient_id == 42
    assert mock_repo_instance.update_status.await_count == 2

class RewindError(Exception):
    """Base class for all Rewind domain errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# --- Auth ---


class EmailAlreadyRegisteredError(RewindError):
    pass


class InvalidCredentialsError(RewindError):
    pass


class PasswordTooShortError(RewindError):
    pass


class NotAuthenticatedError(RewindError):
    pass


# --- Tapes ---


class TapeNotFoundError(RewindError):
    pass


class NotAuthorisedError(RewindError):
    pass


class TapeNotInDraftError(RewindError):
    pass


# --- Tracks ---


class SideFullError(RewindError):
    pass


class TrackNotFoundError(RewindError):
    pass


# --- Spotify ---


class SpotifyNotConfiguredError(RewindError):
    pass


class SpotifyUnavailableError(RewindError):
    pass

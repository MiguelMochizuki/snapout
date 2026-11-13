"""SnapOut: clean up old Snap package revisions."""

from .models import Revision
from .snapd import Snapd

__all__ = ["Revision", "Snapd"]

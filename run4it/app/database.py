"""Database module, including the SQLAlchemy database object
and DB-related utilities."""
import datetime as dt
from sqlalchemy.orm import relationship
from run4it.app.compat import basestring
from run4it.app.extensions import db


# Alias common SQLAlchemy names
Column = db.Column
relationship = relationship
Model = db.Model


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named 'id'
    to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(objectType, record_id):
        """Get record by ID."""
        if any(
                (isinstance(record_id, basestring) and record_id.isdigit(),
                 isinstance(record_id, (int, float))),
        ):
            return objectType.query.get(int(record_id))


def reference_col(tablename, unique=False, nullable=False,
                  pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        unique=unique,
        nullable=nullable, **kwargs)


class TimestampedModel(Model):
    """Abstract Model for models requiring create-/update
    timestamps"""
    __abstract__ = True

    created_at = Column(db.DateTime,
                        nullable=False,
                        default=dt.datetime.utcnow)

    updated_at = Column(db.DateTime,
                        nullable=False,
                        default=dt.datetime.utcnow)

from sqlalchemy import inspect


def model_to_dict(model):
    """
    Converts a SQLAlchemy model instance to a dictionary using SQLAlchemy inspection.

    Args:
        model: The SQLAlchemy model instance to convert.

    Returns:
        A dictionary containing the model's attributes and values.
    """
    columns = [c.key for c in inspect(model).mapper.column_attrs]
    return {attr: getattr(model, attr) for attr in columns}

from sqlalchemy import or_, asc, desc
from sqlalchemy.exc import SQLAlchemyError

from base.db.database import Database
from base.utils.pagination import get_page_info
from base.vo.country_vo import CountryVO

database = Database()
engine = database.get_db_connection()


class MysqlCommonQuery:
    """Generic MySQL repository for common database operations.

    Company Name: Softvan Pvt Ltd
    """

    @staticmethod
    def insert_query(create_object):
        """
        Purpose:
            Insert a new record into the database.

        Request:
            create_object: SQLAlchemy ORM object to be inserted.

        Response:
            Returns the inserted object with refreshed state from the database.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        try:
            session.add(create_object)
            session.commit()
            session.refresh(create_object)
            return create_object
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    @staticmethod
    def get_all_query(table_name):
        """
        Purpose:
            Retrieve all non-deleted records from the specified table.

        Request:
            table_name: SQLAlchemy ORM model class representing the table.

        Response:
            List of all records where is_deleted is False.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        table_data = (
            session.query(table_name).filter(table_name.is_deleted == False).all()
        )
        return table_data

    @staticmethod
    def soft_delete_query(table_name, table_id, entity_id):
        """
        Purpose:
            Soft delete a record by setting its 'is_deleted' flag to True.

        Request:
            table_name: SQLAlchemy ORM model class representing the table.
            table_id: ORM column representing the primary key.
            entity_id: ID of the record to soft delete.

        Response:
            Returns the updated record after soft deletion.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        table_data = (
            session.query(table_name)
            .filter(table_id == entity_id, table_name.is_deleted == False)
            .first()
        )
        table_data.is_deleted = True
        session.commit()
        return table_data

    @staticmethod
    def get_by_id_query(table_name, table_id, entity_id):
        """
        Purpose:
            Retrieve a single record by its primary key excluding soft-deleted entries.

        Request:
            table_name: SQLAlchemy ORM model class representing the table.
            table_id: ORM column representing the primary key.
            entity_id: ID of the record to retrieve.

        Response:
            The matching record or None if not found.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        table_data = (
            session.query(table_name)
            .filter(table_id == entity_id, table_name.is_deleted == False)
            .first()
        )
        return table_data

    @staticmethod
    def update_query(update_record):
        """
        Purpose:
            Update an existing record in the database.

        Request:
            update_record: ORM object with updated fields.

        Response:
            Returns the updated record after commit.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        session.merge(update_record)
        session.flush()
        session.commit()
        session.close()
        return update_record

    @staticmethod
    def get_record_by_field(model, field_name, value):
        """
        Purpose:
            Retrieve a single record matching a specific field value.

        Request:
            model: SQLAlchemy ORM model class.
            field_name: String name of the field to filter by.
            value: Value to match in the field.

        Response:
            The matching record or None if not found.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        user_data = (
            session.query(model)
            .filter(getattr(model, field_name) == value)
            .filter(model.is_deleted == False)
            .first()
        )
        print(f"user_data{user_data}")
        session.close()
        return user_data

    @staticmethod
    def update_login_status(
        model_class, table_id, model_id, current_login_status: bool
    ):
        """
        Purpose:
            Update the login status of a user.

        Request:
            model_class: ORM model class representing the user.
            table_id: ORM primary key column.
            model_id: ID of the user to update.
            current_login_status: Boolean status to set.

        Response:
            Returns the updated user object.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)

        existing_user = session.query(model_class).filter(table_id == model_id).first()

        if existing_user:
            existing_user.login_status = current_login_status
            session.commit()

        session.close()
        return existing_user

    @staticmethod
    def get_all_with_filters(page_info):
        """
        Purpose:
            Retrieve paginated, searchable, and sortable records from a table.

        Request:
            page_info: Dictionary containing
                - model: ORM model class
                - search_fields: list of field names to search
                - search_value: search string
                - page_number: current page number
                - page_size: number of records per page
                - sort_by: field name to sort by
                - sort_as: 'asc' or 'desc'

        Response:
            Dictionary with
                - items: list of retrieved records
                - page_info: pagination metadata

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)

        model = page_info["model"]
        search_fields = page_info.get("search_fields", [])
        search_value = page_info.get("search_value", "")
        page_number = page_info.get("page_number", 1)
        page_size = page_info.get("page_size", 10)
        sort_by = page_info.get("sort_by", "id")
        sort_as = page_info.get("sort_as", "asc")

        query = session.query(model).filter(model.is_deleted == False)

        if search_value and search_fields:
            search_term = f"%{search_value.lower()}%"
            query = query.filter(
                or_(
                    *[
                        getattr(model, field).ilike(search_term)
                        for field in search_fields
                    ]
                )
            )

        if hasattr(model, sort_by):
            sort_column = getattr(model, sort_by)
            query = query.order_by(
                asc(sort_column) if sort_as == "asc" else desc(sort_column)
            )
        else:
            query = query.order_by(model.id.asc())

        total = query.count()
        offset = (page_number - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        session.close()

        return {
            "items": items,
            "page_info": get_page_info(total, page_number, page_size),
        }

    @staticmethod
    def fetch_email_by_login_username(register_vo, login_vo, username, loginId):
        """
        Purpose:
            Fetch the registered email address for a given login username.

        Request:
            register_vo: ORM model representing registration information.
            login_vo: ORM model representing login information.
            username: Username string to query.
            loginId: Relationship key between register_vo and login_vo.

        Response:
            Tuple containing the email or None.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        result = (
            session.query(register_vo.register_email)
            .join(login_vo, register_vo.register_login_vo == loginId)
            .filter(login_vo.login_username == username)
            .first()
        )
        print(f"result{result}")
        return result

    @staticmethod
    def get_country_id_by_name(name: str):
        """
        Purpose:
            Retrieve country ID by country name.

        Request:
            name: String name of the country.

        Response:
            Integer country_id if found; otherwise None.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        try:
            country = (
                session.query(CountryVO).filter(CountryVO.country_name == name).first()
            )
            return country.country_id if country else None
        finally:
            session.close()

    @staticmethod
    def get_role(table, pk_column, value):
        """
        Purpose:
            Retrieve a role record by its primary key value.

        Request:
            table: ORM model class representing roles.
            pk_column: Primary key column of the table.
            value: Value to search for.

        Response:
            The matching role record or None.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        result = session.query(table).filter(pk_column == value).first()
        return result

    @staticmethod
    def get_by_membership_id(table_name, membership_id):
        """
        Purpose:
            Retrieve a record by membership ID.

        Request:
            table_name: ORM model class representing the table.
            membership_id: Membership ID to search for.

        Response:
            The matching record or None if not found.

        Company Name: Softvan Pvt Ltd
        """
        session = database.get_db_session(engine)
        db_data = (
            session.query(table_name).filter_by(membership_id=membership_id).first()
        )

        return db_data

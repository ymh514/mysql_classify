import json
import os

import pymysql
from PIL import Image, ExifTags

from database.common_lib import sql_string, dictionary

EXIST_DEBUG_FLAG = 1


class DatabaseHandler:
    """ Database handler only new once """

    def __init__(self):
        """ Initial Class """

        self._database = pymysql.connect(
            "localhost", "root", "12345678", "mydatabase", charset="utf8")
        self._cursor = self._database.cursor()

        self._sql = sql_string.SqlString()
        self._dict = dictionary.Dictionary()
        self._thumbnail_path = ""

    def _send_sql_cmd(self, sql_str):
        """ Used to Send SQL Command """
        try:
            self._cursor.execute(sql_str)
            self._database.commit()
        except Exception as e:
            print('-----')
            print(e)
            print(sql_str)
            print('-----')

        else:
            self._database.commit()

    def clear_all(self):
        """ Reset database & Create summary & users table """
        # Reset database
        drop_str, create_str = self._sql.get_initial_str()
        self._send_sql_cmd(drop_str)
        self._send_sql_cmd(create_str)
        self._database.select_db("mydatabase")

        # Create summary table
        sql_str = self._sql.get_create_summary_table_str()
        self._send_sql_cmd(sql_str)

        # Create users table
        sql_str = self._sql.get_create_user_table_str()
        self._send_sql_cmd(sql_str)

    def _new_user(self, user_name):
        """ When new user get in, insert to users table & create user's file_type table """
        # Insert user to users table
        sql_str = self._sql.get_insert_user_table_str(user_name)
        self._send_sql_cmd(sql_str)

        # Create (user)_(file_type) table
        self._create_user_type_table(user_name)

    def _create_user_type_table(self, user_name):
        """ Create (user)_(file_type) table """
        # Create Tables
        for file_type in self._dict.type_tablename_dict:
            # create each table
            type_sql_str = self._sql.get_create_type_table_str(user_name, file_type)
            self._send_sql_cmd(type_sql_str)

    def _insert_folder_to_tables(self, path, folder, user_name):
        """ Insert folder to tables """
        insert_summary_sql_str, insert_type_sql_str = \
            self._sql.get_insert_folder_str(path, folder, user_name)

        self._send_sql_cmd(insert_summary_sql_str)
        self._send_sql_cmd(insert_type_sql_str)

    def _set_thumbnail(self, path, file, user_name):
        """ Generate thumbnail """
        #  Generate thumbnail for image
        get_summary_id_sql = "SELECT id,type FROM summary WHERE name=\""
        get_summary_id_sql += file
        get_summary_id_sql += "\" AND path=\""
        get_summary_id_sql += path
        get_summary_id_sql += "\";"

        self._send_sql_cmd(get_summary_id_sql)

        summary_id = 0
        file_type = ""
        result = self._cursor.fetchall()
        for row in result:
            # row[1] = user
            summary_id = row[0]
            file_type = row[1]
        self._database.commit()

        if file_type == 'image':
            full_path = os.path.join(path, file)

            image = Image.open(full_path)
            # prevent rotation
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = dict(image._getexif().items())

                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)

            except (AttributeError, KeyError, IndexError):
                # cases: image don't have getexif
                pass

            image.thumbnail((64, 64))
            save_str = self._thumbnail_path + "/"
            save_str += user_name

            # check dir
            if not os.path.isdir(save_str):
                os.mkdir(save_str)

            save_str += "/"
            save_str += str(summary_id)
            save_str += ".jpg"
            image.save(save_str)
            image.close()

    def _insert_file_to_tables(self, path, file, user_name):
        """ Insert File to tables """

        # 先確定是否有在裡面
        check_sql = self._sql.get_check_file_already_exist_str(path, file, user_name)
        self._send_sql_cmd(check_sql)
        summary_id = 0
        result = self._cursor.fetchall()
        for row in result:
            # row[1] = user
            summary_id = row[0]
        self._database.commit()

        if summary_id == 0:
            # not exist
            insert_summary_sql_str, insert_type_sql_str = \
                self._sql.get_insert_tables_str(path, file, user_name)

            self._send_sql_cmd(insert_summary_sql_str)
            self._send_sql_cmd(insert_type_sql_str)
        else:
            # already exist
            update_summary_sql_str, update_type_sql_str = self._sql.get_update_file_table_str(path, file, user_name)
            self._send_sql_cmd(update_summary_sql_str)
            self._send_sql_cmd(update_type_sql_str)

        self._set_thumbnail(path, file, user_name)

    def _check_path(self, path_or_file, user_name):
        """ When initial search path layer by layer to find files & add """
        if os.path.isdir(path_or_file):
            # input is a path
            path = path_or_file
            file_list = os.listdir(path)
            for file in file_list:
                full_path = os.path.join(path, file)
                if os.path.isdir(full_path):
                    folder = file
                    # call insert
                    self._insert_folder_to_tables(path, folder, user_name)
                    self._check_path(full_path, user_name)
                elif os.path.isfile(full_path):
                    if not file.startswith('.'):
                        # '.' start file don't do
                        self._insert_file_to_tables(path, file, user_name)
        else:
            # input is a file
            path, file = os.path.split(path_or_file)
            if not file.startswith('.'):
                # '.' start file don't do
                self._insert_file_to_tables(path, file, user_name)

    def _get_json_payload(self, path=None, data=None, status=0, message='sucess'):
        """ Form defined format json payload """
        root = {}
        root['status'] = status
        root['message'] = message
        if data is not None:
            root['data'] = data
        if path is not None:
            root['path'] = path
        return json.dumps(root)

    def initial_database_handler(self, path, user_name):
        """ Initial database handler : first time search path & create table """
        upper_path = os.path.abspath(os.path.join(os.path.dirname(path), '.'))
        upper_path += "/mysql_resize"
        # check dir
        if not os.path.isdir(upper_path):
            os.mkdir(upper_path)
        self._thumbnail_path = upper_path

        # First user
        self._new_user(user_name)

        self._check_path(path, user_name)
        return self._get_json_payload()

    def update_database_handler(self, path, user_name):
        """ Update new path or file """
        sql_str = self._sql.get_select_user_table_str()
        self._send_sql_cmd(sql_str)

        user_dict = []
        result = self._cursor.fetchall()
        for row in result:
            # row[1] = user
            user_dict.append(row[1])

        self._database.commit()

        # inside or not
        if user_name not in user_dict:
            self._new_user(user_name)

        # check path and insert files
        self._check_path(path, user_name)
        return self._get_json_payload()

    def get_user_type_table(self, user_name, file_type):
        """ Return user's (type) table with id """
        sql_str = self._sql.get_user_file_type_str(user_name, file_type)
        self._send_sql_cmd(sql_str)

        if self._cursor.rowcount > 0:

            data_list = []
            result = self._cursor.fetchall()
            for row in result:
                temp = dict()
                temp['id'] = row[0]
                temp['file_name'] = row[1]
                temp['time'] = row[2]
                temp['type'] = file_type
                data_list.append(temp)

            self._database.commit()

            pack_data_list = dict()
            pack_data_list['list'] = data_list
            return self._get_json_payload(data=pack_data_list)
        else:
            return self._get_json_payload(path="", status=-2, message="not found in database")

    def get_files_under_folder(self, folder_path):
        """ Return files under folder with id """
        sql_str = self._sql.get_files_under_folder_str(folder_path)
        self._send_sql_cmd(sql_str)

        if self._cursor.rowcount > 0:
            data_list = []
            result = self._cursor.fetchall()
            for row in result:
                temp = dict()
                temp['id'] = row[0]
                temp['file_name'] = row[1]
                temp['time'] = row[2]
                temp['type'] = row[3]
                data_list.append(temp)

            self._database.commit()

            pack_data_list = dict()
            pack_data_list['list'] = data_list
            return self._get_json_payload(data=pack_data_list)
        else:
            return self._get_json_payload(path="", status=-2, message="not found in database")


    def get_file_path_with_id(self, file_id):
        """ Return file's path with file id (summary table) """
        sql_str = self._sql.get_file_path_with_id_str(file_id)
        self._send_sql_cmd(sql_str)

        if self._cursor.rowcount > 0:
            result = self._cursor.fetchall()

            return_path = result[0][0] + "/"
            return_path += result[0][1]

            self._database.commit()
            return self._get_json_payload(path=return_path)
        else:
            return self._get_json_payload(path="", status=-2, message="not found in database")

    def get_image_thumbnail(self, image_id):
        """ Return image thumbnail with id """
        sql_str = self._sql.get_image_thumbnail_str(image_id)
        self._send_sql_cmd(sql_str)

        # 有抓到東西
        if self._cursor.rowcount > 0:
            result = self._cursor.fetchall()
            user_name = result[0][0]
            file_type = result[0][1]
            if file_type is not 'image':
                return self._get_json_payload(path="", status=-1, message="there is no thumbnail for this type")
            thumbnail_path = self._thumbnail_path + "/"
            thumbnail_path += user_name
            thumbnail_path += "/"
            thumbnail_path += str(image_id)
            thumbnail_path += ".jpg"
            return self._get_json_payload(path=thumbnail_path)
        else:
            return self._get_json_payload(path="", status=-2, message="not found in database")

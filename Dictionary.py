class Dictionary:
    type_tablename_dict = {
        'image': 'image',
        'video': 'video',
        'music': 'music',
        'file': 'file',
        'folder':'folder'}
    type_dict = {
        'mp3': 'music',
        'aac': 'music',
        'flac': 'music',
        'ogg': 'music',
        'wma': 'music',
        'm4a': 'music',
        'aiff': 'music',
        'wav': 'music',
        'amr': 'music',
        'flv': 'video',
        'ogv': 'video',
        'avi': 'video',
        'mp4': 'video',
        'mpg': 'video',
        'mpeg': 'video',
        '3gp': 'video',
        'mkv': 'video',
        'ts': 'video',
        'webm': 'video',
        'vob': 'video',
        'wmv': 'video',
        'png': 'image',
        'jpeg': 'image',
        'gif': 'image',
        'jpg': 'image',
        'bmp': 'image',
        'svg': 'image',
        'webp': 'image',
        'psd': 'image',
        'tiff': 'image',
        'txt': 'file',
        'pdf': 'file',
        'doc': 'file',
        'docx': 'file',
        'odf': 'file',
        'xls': 'file',
        'xlsv': 'file',
        'xlsx': 'file',
        'ppt': 'file',
        'pptx': 'file',
        'ppsx': 'file',
        'odp': 'file',
        'odt': 'file',
        'ods': 'file',
        'md': 'file',
        'json': 'file',
        'csv': 'file',
        'MP3': 'music',
        'AAC': 'music',
        'FLAC': 'music',
        'OGG': 'music',
        'WMA': 'music',
        'M4A': 'music',
        'AIFF': 'music',
        'WAV': 'music',
        'AMR': 'music',
        'FLV': 'video',
        'OGV': 'video',
        'AVI': 'video',
        'MP4': 'video',
        'MPG': 'video',
        'MPEG': 'video',
        '3GP': 'video',
        'MKV': 'video',
        'TS': 'video',
        'WEBM': 'video',
        'VOB': 'video',
        'WMV': 'video',
        'PNG': 'image',
        'JPEG': 'image',
        'GIF': 'image',
        'JPG': 'image',
        'BMP': 'image',
        'SVG': 'image',
        'WEBP': 'image',
        'PSD': 'image',
        'TIFF': 'image',
        'TXT': 'file',
        'PDF': 'file',
        'DOC': 'file',
        'DOCX': 'file',
        'ODF': 'file',
        'XLS': 'file',
        'XLSV': 'file',
        'XLSX': 'file',
        'PPT': 'file',
        'PPTX': 'file',
        'PPSX': 'file',
        'ODP': 'file',
        'ODT': 'file',
        'ODS': 'file',
        'MD': 'file',
        'JSON': 'file',
        'CSV': 'file'}

    def getFileType(self,file_extension):
        """ Return file extension's type """

        if file_extension in self.type_dict:
            return self.type_dict[file_extension]
        else:
            return 'file'

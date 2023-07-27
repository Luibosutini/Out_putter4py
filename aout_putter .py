import sys
import requests
import json
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QListWidget, QMessageBox


class MemoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.memo_list = []
        self.tag_list = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.login_layout = QHBoxLayout()
        self.login_label = QLabel("Qiitaアクセストークン:")
        self.login_input = QLineEdit()
        self.login_layout.addWidget(self.login_label)
        self.login_layout.addWidget(self.login_input)

        self.title_layout = QHBoxLayout()
        self.title_label = QLabel("タイトル:")
        self.title_input = QLineEdit()
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.title_input)

        self.memo_label = QLabel("メモを入力してください:")
        self.memo_input = QLineEdit()
        self.tag_label = QLabel("Tagを入力してください:")
        self.tag_input = QLineEdit()
        self.private_checkbox = QCheckBox("非公開（プライベート）にする")
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_memo)

        self.memo_list_widget = QListWidget()

        self.get_button = QPushButton("Qiitaに投稿")
        self.get_button.clicked.connect(self.post_to_qiita)

        layout.addLayout(self.login_layout)
        layout.addLayout(self.title_layout)
        layout.addWidget(self.memo_label)
        layout.addWidget(self.memo_input)
        layout.addWidget(self.tag_label)
        layout.addWidget(self.tag_input)
        layout.addWidget(self.private_checkbox)
        layout.addWidget(self.save_button)
        layout.addWidget(self.memo_list_widget)
        layout.addWidget(self.get_button)

        self.setLayout(layout)
        self.setWindowTitle("Memo App")
        self.show()

    def save_memo(self):
        memo_text = self.memo_input.text()
        tag_text = self.tag_input.text()
        if memo_text and tag_text:
            self.memo_list.append(memo_text)
            self.tag_list.append(tag_text)
            title_text = self.title_input.text()
            is_private = self.private_checkbox.isChecked()
            visibility = "private" if is_private else "public"
            self.memo_list_widget.addItem(f"{title_text}: {memo_text} [Tag: {tag_text}] - {visibility}")
            self.memo_input.clear()
            self.tag_input.clear()
            self.title_input.clear()

    def post_to_qiita(self):
        selected_items = self.memo_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "エラー", "メモを選択してください。")
            return

        qiita_token = self.login_input.text()
        if not qiita_token:
            QMessageBox.warning(self, "エラー", "Qiitaアクセストークンを入力してください。")
            return

        for item in selected_items:
            text_with_tag_visibility = item.text()
            title, memo_text, tag_text, visibility = self.extract_title_memo_tag_and_visibility(text_with_tag_visibility)
            response = self.create_qiita_post(title, memo_text, tag_text, visibility, qiita_token)

            if response and response.status_code == 201:
                QMessageBox.information(self, "成功", f"'{title}' をQiitaに投稿しました！")
            else:
                QMessageBox.warning(self, "エラー", f"'{title}' の投稿に失敗しました。Qiitaのアクセストークンを確認してください。")
                print("ステータスコード:", response.status_code)
                print("レスポンス内容:", response.json())

    def extract_title_memo_tag_and_visibility(self, text_with_tag_visibility):
        visibility = text_with_tag_visibility.endswith("private")
        text_with_tag_visibility = text_with_tag_visibility[0 : text_with_tag_visibility.rfind(" - ")]
        
        tag = re.search("\[Tag: .+]", text_with_tag_visibility)
        tag_text = text_with_tag_visibility[tag.start() + 6 : tag.end() - 1]
        text_with_tag_visibility = text_with_tag_visibility[0 : text_with_tag_visibility.rfind("[Tag: ")]
        
        title_and_text = text_with_tag_visibility.split(": ")
        title = title_and_text[0]
        memo_text = title_and_text[1]
        
        return title, memo_text, tag_text, visibility


    def create_qiita_post(self, title, text, tag, visibility, qiita_token):
        qiita_api_url = "https://qiita.com/api/v2/items"

        headers = {
            "Authorization": f"Bearer {qiita_token}",
            "Content-Type": "application/json",
        }

        data = {
            "body": text,
            "tags": [{"name": tag}],
            "title": title,
            "private": visibility
        }

        try:
            response = requests.post(qiita_api_url, headers=headers, data=json.dumps(data))
            return response
        except requests.exceptions.RequestException as e:
            print(e)
            return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoApp()
    sys.exit(app.exec_())

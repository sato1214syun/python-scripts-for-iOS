import re
from typing import Optional, List, Dict, Tuple


def delete_tag(s):
    regex_pattern = r"<.*?>|\[.*?\]"
    s = re.sub(regex_pattern, "", s)
    """ recursive processing """
    if re.search(regex_pattern, s):
        delete_tag(s)
    else:
        return s


def ReorganizeText(text: str) -> str:
    text = re.sub(r"[\[\(].*?[\)\]]\.?", "", text).strip()
    text = re.sub(r"([^\.,a-zA-Z0-9])\s+([^\.,a-zA-Z0-9])", r"\1\2", text)
    if len(text) > 2:
        if text[0] == "（" and text[-1] != "）":
            text += "）"
        if text[0] == "(" and text[-1] != ")":
            text += ")"
        if text[0] != "（" and text[-1] == "）":
            text = "（" + text
        if text[0] != "(" and text[-1] == ")":
            text = "（" + text
    return text


def ParseText(
    text_list: List[str],
) -> Tuple[Optional[Dict[str, str]], List[Dict[str, str]], List[str]]:
    block_type: Optional[str] = "quotes"  # part2(その2)以降の記事はセリフのブロックから始まるのでquotesに設定
    # is_skip_line_cnt: int = 0
    eng_title: Optional[str] = None
    jpn_title: Optional[str] = None
    ori_title_in_jpn: Optional[str] = None
    title: Optional[Dict[str, str]] = None
    subtitle: List[Dict[str, str]] = []
    commentary: List[str] = []
    speaker: Optional[str] = None
    en_quote: Optional[str] = None
    jp_quote: Optional[str] = None
    speaker_pattern1 = r"^([ \
        \u2E80-\u2FDF \
        \u3005-\u3007 \
        \u3400-\u4DBF \
        \u4E00-\u9FFF \
        \uF900-\uFAFF \
        \U00020000-\U0002EBEF \
        ぁ-ゟァ-ヴー・ \
        ]+):.*$"
    speaker_pattern2 = r"^([ \
        \u2E80-\u2FDF \
        \u3005-\u3007 \
        \u3400-\u4DBF \
        \u4E00-\u9FFF \
        \uF900-\uFAFF \
        \U00020000-\U0002EBEF \
        ぁ-ゟァ-ヴー・ \
        ]+):$"

    temp_commentary: str = ""
    for line in text_list:
        # セリフが突然出てきたときに対応
        if block_type == "commentary" and re.match(speaker_pattern1, line) is not None:
            block_type = "quotes"
            speaker = None
        # もしシーズン番号などがあればそのブロックはtitle
        if re.match(r"シーズン\s*[０-９0-9]+\s*第\s*[０-９0-9]+\s*話", line):
            block_type = "title"
            continue
        if block_type == "title":
            if eng_title is None or jpn_title is None:
                temp_title_list = line.replace("）", "").split("（")
                eng_title, jpn_title = [title.strip() for title in temp_title_list]
                continue
            if ori_title_in_jpn is None:
                ori_title_in_jpn = line.split("「")[1].replace("」", "")
                continue
            if line == "区切り":
                block_type = "quotes"
                continue

        # セリフのブロックquotes
        if block_type == "quotes":
            line = ReorganizeText(line)
            if line == "":
                continue
            if line.find("[Scene: ") == 0:  # 場面の説明なので飛ばす
                # is_skip_line_cnt = 1  # 次の1行も場面の解説(日本語)なので飛ばす
                continue
            # 話者の抽出(漢字、ひらがな、カタカナ)
            if re.match(speaker_pattern2, line) is not None:
                # eng_quoteとjpn_quoteがNoneでない場合(直前にセリフがある場合)はリストに格納
                if (
                    speaker is not None
                    and en_quote is not None
                    and jp_quote is not None
                ):
                    subtitle.append(
                        {"speaker": speaker, "en": en_quote, "jp": jp_quote}
                    )
                # 話者の名前を入れて、セリフを初期化
                speaker = line.replace(":", "")
                en_quote = None
                jp_quote = None
                continue
            # セリフ(英語)の抽出
            if "<strong>" in line:
                temp_quote = delete_tag(re.sub(r"<br/?>", " ", line))
                if en_quote is None:
                    en_quote = temp_quote
                else:
                    en_quote += " {}".format(temp_quote)
                continue
            # brackets(括弧)で囲まれている場合は、日本語のセリフの場合と、英語の場面説明の場合があるので判別
            if re.match(r"^[\(（].+[\)）]$", line) is not None:
                temp_quote = re.sub(r"^[ -~\n]+$", "", line).strip()
                if re.match(
                    r"^[a-zA-Z0-9!\-\/:-@¥[-`{-~\s]*$", temp_quote
                ):  # 英数字記号のみの場合は英語の場面説明
                    continue
                else:
                    temp_quote = re.sub(r"^[\(（]|[\)）]$", "", temp_quote)

                    if jp_quote is None:
                        jp_quote = temp_quote
                    else:
                        jp_quote += " {}".format(temp_quote)
                    continue
            if line == "区切り":
                # eng_quoteとjpn_quoteがNoneでない場合(直前にセリフがある場合)はリストに格納
                if (
                    speaker is not None
                    and en_quote is not None
                    and jp_quote is not None
                ):
                    subtitle.append(
                        {"speaker": speaker, "en": en_quote, "jp": jp_quote}
                    )
                block_type = "commentary"
                continue

        # ブログの作者の解説
        if block_type == "commentary":
            if line == "区切り":
                if temp_commentary == "":
                    continue
                temp_commentary = re.sub(
                    r"([a-zA-Z0-9\.,])<br/>", r"\1 ", temp_commentary
                )
                temp_commentary = delete_tag(temp_commentary)
                commentary.append(temp_commentary)
                temp_commentary = ""
                continue
            else:
                temp_commentary += line
                continue

    if eng_title is not None and jpn_title is not None and ori_title_in_jpn is not None:
        title = {
            "en": eng_title,
            "jp": jpn_title,
            "jp_ori": ori_title_in_jpn,
        }
    else:
        title = None
    return (
        title,
        subtitle,
        commentary,
    )

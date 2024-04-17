import unittest
from unittest.mock import MagicMock, patch

import sys
sys.path.append('html')

from filehandler import sanitize_filename

class TestSanitizeFilename(unittest.TestCase):
    """
    Test the sanitize_string function.
    """

    def test_string_with_whitelisted_characters(self):
        """
        Test with a string containing only whitelisted characters.
        """
        input_string = "abc123_-."
        expected_output = "_abc123_-."
        self.assertEqual(sanitize_filename(input_string)[8:], expected_output)

    def test_string_with_non_whitelisted_characters(self):
        """
        Test with a string containing non-whitelisted characters.
        """
        input_string = "abc!@#123_$%^&"
        expected_output = "_abc123_"
        self.assertEqual(sanitize_filename(input_string)[8:], expected_output)

    def test_empty_string(self):
        """
        Test with an empty string.
        """
        input_string = ""
        expected_output = "_"
        self.assertEqual(sanitize_filename(input_string)[8:], expected_output)

    def test_string_with_only_non_whitelisted_characters(self):
        """
        Test with a string containing only non-whitelisted characters.
        """
        input_string = "!@#$%^&*()+{=}[|\:;\"'<>,?/~`¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮį"
        input_string += "丨丿乛亅乙乚凵匚冂冖冫几勹匸卂卄卌卍厶厽凵夂夊夕夨夬妀妟妸妺妼妯妾妿姃姄姅姈姌姕姖姞姟姠姢姤姦姧姩姪姫姭姯姰姲姳姴姵姶姷姸姹姺姻姼姽姾姿娀娂娃娄娅娈娉娊娌娍娎娏娐娒娓娕娖娗娙娚娛娝娞娟娠娢娣娤娦娧娨娩娪娫娬娭娮娯娰娳娵娷娸娹娺娻娽娾娿婀婁婃婄婅婇婈婋婎婏"
        input_string += "婑婓婔婖婗婘婙婚婛婜婝婞婟婠婡婣婤婥婦婧婨婩婫婬婭婮婯婰婱婲婳婴婵婶婷婸婹婺婻婼婽婾婿媀媁媃媄媅媆媇媈媉媊媋媌媍媎媏媐媑媒媓媔媕媖媗媘媙媛媜媝媞媟媠媡媢媣媤媥媦媧媨媩媪媫媬媭媮媯媰媱媴媶媷媸媹媺媻媼媽媾媿嫀嫃嫄嫅嫆嫇嫈嫊嫋"
        input_string += "嫌嫍嫎嫏嫐嫑嫒嫓嫔嫕嫖嫗嫘嫙嫚嫛嫜嫝嫞嫟嫠嫡嫢嫣嫤嫥嫧嫨嫩嫪嫬嫭嫮嫯嫰嫱嫲嫳嫴嫵嫶嫷嫸嫹嫺嫼嫽嫾嫿嬀嬁嬂嬃嬄嬅嬆嬇嬈嬉嬊嬋嬌嬍嬎嬐嬑嬒嬓嬔嬕嬖嬗嬘嬙嬚嬛嬜嬝嬞嬟嬠嬡嬢嬣嬤嬥嬦嬧嬨嬪嬫嬬嬭嬮嬯嬰嬱嬳嬴嬵嬶嬷嬸嬹嬻嬼嬽嬾嬿孀孁"
        input_string += "孂孃孄孆孇孈孉孊孋孍孎孏子孑孒孓孖字孙孚孛孜孞孠孡孢季孤孥孧孨孩孪孫孬孭孮孯孰孱孲孳孴孵孶孷學孹孻孼孽孾孿宀宄宆宊宍宐宑宒宓宔宖実宥宧宨宩宭宮宯宰宱宲害宵"
        input_string += "家宷宸容宺宻宼宽宾寁寃寈寉寊寋寍寎寏寐寑寔寕寖寗寘寙寚寛寜寝寞寠寡寢寣寤寥實寧寨審寪寫寬寭寮寯寰寱寲寳寴寵寷寽対尀専尃尅將專尋尌對導尐尒尓"
        input_string += "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        input_string += "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        input_string += "���"

        expected_output = "_"
        self.assertEqual(sanitize_filename(input_string)[8:], expected_output)

if __name__ == "__main__":
    unittest.main()

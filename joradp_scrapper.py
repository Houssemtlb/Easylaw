
"""
1. open https://www.joradp.dz/HAR/Index.htm
2. get this element:
<a href="/JRN/ZA2024.htm" title="عرض الجرائد" target="FnCli">الـجـرائــد</a>
3. get the href from the element

4. for each year starting from 2024  which we got from the above element to 1964:
we want to :
make a request with the year in the path:

curl "https://www.joradp.dz/JRN/ZA2024.htm" -H 
"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0" 
-H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" 
-H "Accept-Language: en-US,en;q=0.5" -H "Accept-Encoding: gzip, deflate, br" -H "Connection: keep-alive" 
-H "Referer: https://www.joradp.dz/HAR/ATitre.htm" 
-H "Upgrade-Insecure-Requests: 1" 
-H "Sec-Fetch-Dest: frame" 
-H "Sec-Fetch-Mode: navigate" 
-H "Sec-Fetch-Site: same-origin" 
-H "Sec-Fetch-User: ?1" 
-H "TE: trailers"

The response is like:

<html>
 <head>
  <title>Ã.Ú.Í ÇáÌÒÇÆÑ</title>
  <meta name="Description" content="ÇáÌÑíÏÉ ÇáÑÓÜãíÉ ááÌãåæÑíÉ ÇáÌÒÇÆÑíÉ">
  <meta http-equiv="Content-Type" content="text/html; charset=windows-1256">
  <meta http-equiv="Content-Language" content="ar">
  <meta http-equiv="PRAGMA" content="NO-STORE">
  <link rel="stylesheet" href="/CSS/CssAr.css" type="text/css">
  <style type="text/css"><!--
   td {font-family: Arial; font-size: 10pt; font-style: normal; font-weight: bold; color: Black}
   th {font-family: Arial; font-size: 10pt; font-style: normal; font-weight: bold; color: #343331}
   #tit {font-family: Arial; font-size: 12pt; font-style: normal; font-weight: bold; color: Black}
  --></style>
  <SCRIPT LANGUAGE="JavaScript" SRC="/JVS/Journal.js"></script>
  <SCRIPT LANGUAGE=JavaScript>
  <!--
  function MaxWin(Adr)
  { NewWin=window.open("","","");
    if (document.all)
    { NewWin.moveTo(0,0);
      NewWin.resizeTo(screen.width,screen.height); };
    NewWin.location="/FTP/jo-arabe/2024/A2024"+Adr+".pdf";
  }
  // -->
  </script>
 </head>
<body background="/IMG/Backmm.jpg" bgproperties="fixed">
 <div align="right" dir="rtl">
  <table align="center width="100%" cellpadding=0 cellspacing=0 border=0>
  <tr><td></td></tr>
 <tr><td id=Titre0>ÊÍãíÜÜá ÇáÜÌÜÑÇÆÜÏ</td></tr>
 <tr><td valign="top"><img src="/IMG/separe-ver.gif" width="100%" height=4>
  </td></tr></table><center>
 <table align="center width="100%" cellpadding=0 cellspacing=0 border=0>
  <tr><td>
    <form name="zFrm" target=FnCli>ÇáÜÓÜäÜÉ
     <select name="zAnn" onChange="JrnDwn(zFrm,zAnn,'A')">
      <option selected>2024
      <option>2023
        // years options
      <option>1964
     </select>
    </form>

</td><td width=10, height=40></td><td>
 <form name="zFrm2" target=FnCli2>ÇáÌÑíÏÉ ÑÞã :
     <select name="znjo" onChange="Livejo(zFrm2,znjo,'arabe/2024/A20240')">

      <option>
      // we want to get this values
<option value="14">14
<option value="11">11
<option value="10">10
<option value="09">09
<option value="08">08
<option value="07">07
<option value="06">06
<option value="05">05
<option value="04">04
<option value="03">03
<option value="02">02
<option value="01">01 
 

     </select>
    </form>
</td></tr><tr></tr></table>
// rest of the html code


and get the options for this year

store each year with its values in a data structure

5. print this datastructure
"""

import scrapy

class JoradpSpider(scrapy.Spider):
    name = 'joradp'
    start_urls = ['https://www.joradp.dz/HAR/Index.htm']

    def parse(self, response):
        # Step 2: Extract href attribute from the specified element
        href = response.css('a[title="عرض الجرائد"]::attr(href)').get()
        
        if href:
            # Step 3: Extract year from the href attribute
            currentYear = int(href.split('ZA')[1].split('.')[0])
            
            # Step 4: Make requests for each year from 2024 to 1964
            for year in range(currentYear, 1963, -1):
                url = f'https://www.joradp.dz/JRN/ZA{year}.htm'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.joradp.dz/HAR/ATitre.htm',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'frame',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'TE': 'trailers',
                }
                yield scrapy.Request(url, headers=headers, callback=self.parse_year, meta={'year': year})

    def parse_year(self, response):
        # Step 5: Extract options for the current year
        options = response.css('form[name="zFrm2"] select[name="znjo"] option')
        year = response.meta['year']
        year_data = {year: [option.attrib['value'] for option in options]}
        print(year_data)
        
        # Step 6: Print the data structure
        self.log(year_data)

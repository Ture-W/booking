Detta projektet är skapat för min egen användning men jag inser att jag kommer möjligtvis att ge andra tillgång till det så jag skriver viktig info här och på sidan.

standalone.py kan köras på din egna maskin och gör samma sak som index.js och app.py gör.
Jag garanterar inte att jag orkar uppdatera standalone.py om jag någon gång uppdaterar det andra eftersom att jag själv inte kommer använda den filen.

Är inloggningsuppgifterna säkra?
Varför behövs en proxy server?

Alla requests som körs genom browsern (alltså med javascript) riskerar att bli blockerade av CORS-policy skit eftersom att requests skickas till andra domän än där den skickas ifrån. Jag lyckades inte skicka en ajax request till HH identity provider servern för att det blev blockerat. För att autentisera din HH identitet behövs browser cookies, därför kan inte en allmän proxy service användas för detta syftet. Jag löste det genom att ha en egen proxy server som jag kan kontrollera CORS polycieransanj på.

Rested.com hostar proxy servern gratis och den är kopplad till mitt konto. Den drar kod direkt från den här github repon, det är alltså open source. /backend mappen inehåller koden som hostas. Är inloggningsuppgifterna säkra? Titta i index.js och app.py så ser du exakt var de hamnar. De skickas till hh för validering och sen försvinner dem. Jag säger att du ändå måste lite på mig för att använda github sidan eftersom att jag egentligen inte riktigt kan bevisa att proxy servern kör på /backend koden.

ANVÄND INTE SIDAN OM DU ÄR RÄDD ATT JAG BEDRAR DIG
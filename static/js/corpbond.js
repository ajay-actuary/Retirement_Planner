function calculateCorpBondAllocation(){
            var a,b,c;
            a=Number(document.getElementById("id_Equity_Percent").value);
            b=Number(document.getElementById("id_GSec_Percent").value);
            c= 100 - (a + b);
            document.getElementById('id_CorpBond_Percent').value = c;
        }


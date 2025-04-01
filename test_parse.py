import re

def parse_DAT(s):
        e=0
        if "DataAnnotation" not in s:
            e=1
        elif "Report Time" in s:
            e=2
        elif "Enter Work Mode" in s:
            e=3

        r=re.compile(r".*\nExpires in:[\s\n]+(?:(\d+) days? )?(?:(\d+) hours?)? ?(?:(\d+) minutes?)?\n[$]\d.*",re.MULTILINE|re.DOTALL)
        mat=r.match(s)
        d=None
        h=None
        m=None
        if mat:
            d,h,m=mat.groups()
            if not d:
                d=0
            if not h:
                h=0
            if not m:
                m=0
        ls=f"log/doom-{e}"
        log=open(ls, "a", encoding="utf-8")

        log.write(f"--- {e} {d} {h} {m} --- \n")
        log.write(f"{s}\n")
        log.close()
        return (e,d,h,m)
        

print(parse_DAT("""DataAnnotation
Expires in: 3 hours 1 minute
$0.00"""))
print(parse_DAT("""DataAnotation
Expires in: 3 hours 1 minute
$0.00"""))



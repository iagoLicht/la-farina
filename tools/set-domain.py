#!/usr/bin/env python3
"""
Point the whole site at a new domain, in one command.

    py tools/set-domain.py lafarinatruck.co.il

Rewrites every absolute address in index.html, robots.txt and sitemap.xml,
and writes the CNAME file GitHub Pages reads. Run it once, after the domain
is bought and the DNS records are in place. It is safe to run twice.

Pass the bare domain, no https and no www. The bare domain is the address
the site answers on; www redirects to it, which GitHub Pages does by itself.
"""
import io, os, re, sys, datetime

FILES = ["index.html", "robots.txt", "sitemap.xml"]
CURRENT_MARKER = "tools/.current-origin"
FALLBACK_ORIGIN = "https://iagolicht.github.io/la-farina"

def die(msg):
    sys.exit("set-domain: " + msg)

def main():
    if len(sys.argv) != 2:
        die("usage: py tools/set-domain.py <domain>, for example lafarinatruck.co.il")

    domain = sys.argv[1].strip().lower()
    domain = re.sub(r"^https?://", "", domain).rstrip("/")
    if domain.startswith("www."):
        die("pass the bare domain without www. www redirects to it automatically.")
    if not re.fullmatch(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+", domain):
        die("that does not look like a domain: " + domain)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    old = FALLBACK_ORIGIN
    if os.path.exists(CURRENT_MARKER):
        old = io.open(CURRENT_MARKER, encoding="utf-8").read().strip() or FALLBACK_ORIGIN
    new = "https://" + domain

    if old == new:
        print("already pointing at " + new + ", nothing to do")
        return

    total = 0
    for name in FILES:
        if not os.path.exists(name):
            print("  skipped %-12s (not present)" % name)
            continue
        s = io.open(name, encoding="utf-8").read()
        n = s.count(old)
        if n:
            s = s.replace(old, new)
            io.open(name, "w", encoding="utf-8", newline="\n").write(s)
        print("  %-12s %d address%s rewritten" % (name, n, "" if n == 1 else "es"))
        total += n

    # sitemap keeps an honest lastmod
    if os.path.exists("sitemap.xml"):
        s = io.open("sitemap.xml", encoding="utf-8").read()
        today = datetime.date.today().isoformat()
        s = re.sub(r"<lastmod>[^<]*</lastmod>", "<lastmod>%s</lastmod>" % today, s)
        io.open("sitemap.xml", "w", encoding="utf-8", newline="\n").write(s)

    # GitHub Pages reads this file to know which domain to answer on
    io.open("CNAME", "w", encoding="utf-8", newline="\n").write(domain + "\n")
    io.open(CURRENT_MARKER, "w", encoding="utf-8", newline="\n").write(new + "\n")

    print("")
    print("  CNAME        %s" % domain)
    print("")
    print("%d addresses now point at %s" % (total, new))
    print("Next: git add -A && git commit && git push origin main")

if __name__ == "__main__":
    main()

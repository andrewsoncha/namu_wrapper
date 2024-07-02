from Namu import Page

dungeon_page = Page('블레이드러너')
print(dungeon_page.get_pure_text())
print([str(internal_link) for internal_link in dungeon_page.get_internal_links()])
print(dungeon_page.get_external_links())

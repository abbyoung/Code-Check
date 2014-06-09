BEGIN TRANSACTION;
INSERT INTO "messages" VALUES(1,'Title','Overuse of title tag. Make sure your page has one informative, descriptive title, using <title>.','titleoveruse');
INSERT INTO "messages" VALUES(2,'Title','Page has no title tag. Make sure your page has one informative, descriptive title, using <title>.','titlenone');
INSERT INTO "messages" VALUES(3,'Redundant Links','Adjacent links on the page go to the same URL. This repetition can be frustrating for a screen reader user. If possible, combine links into one link, and remove redundant links.','redundantlinks');
INSERT INTO "messages" VALUES(4,'Missing Alternative Text','Give each image a clear, descriptive, and succinct alt attribute. Without alternative text, image content will not be usable to screen reader users. If the image information is available in surrounding content or isn’t important to the user, give it an empty/null value (alt=“”).','alttags');
INSERT INTO "messages" VALUES(5,'Headings','No H1 tag. Page is missing <h1>, which provides screen readers with a starting point when reading a page. Give your page a semantic outline, starting with <h1>.','missingh1');
INSERT INTO "messages" VALUES(6,'Headings','No headings present. Page is missing heading tags (h1, h2, h3...), which provide a navigable outline for screen reader users.','noheadings');
INSERT INTO "messages" VALUES(7,'Headings Steps','Heading tags skip more than one step (h1 to h3). Users will get confused and think they’ve missed content. Make sure headings only move one step (h1 to h2).','headingsskip');
INSERT INTO "messages" VALUES(8,'Layout Tables','Possible layout tables detected. Using tables for layout, instead of tabular data, can make content difficult for screen reader users to understand. If a layout table is unavoidable, make sure content reads correctly left to right, top to bottom.','layouttables');
INSERT INTO "messages" VALUES(9,'Empty Links','Link(s) contain no text. Users will not understand the purpose of the link without text that describes its functionality. Remove the empty link or add descriptive text within the link.','emptylink');
INSERT INTO "messages" VALUES(10,'Language','A language is not declared for the document. Declaring a language enables screen readers to read content in the appropriate language and automatically translate it.','language');
INSERT INTO "messages" VALUES(11,'Missing Input Label','An <input> tag does not have properly associated label text. If a form control is missing an associated text label, the purpose of the form control may not be known by users. Add a <label> element to associate it with its form control. If the label isn''t visible, add an associated label, descriptive title attritubute to the form control, or reference the label using ''aria-labelledby''.','inputlabel');
INSERT INTO "messages" VALUES(12,'Missing Select Label','A <select> tag does not have properly associated label text. If a form control is missing an associated text label, the purpose of the form control may not be known by users. Add a <label> element to associate it with its form control. If the label isn''t visible, add an associated label, descriptive title attritubute to the form control, or reference the label using ''aria-labelledby''.','selectlabel');
INSERT INTO "messages" VALUES(13,'Missing Text Area Label','A <textarea> tag does not have properly associated label text. If a form control is missing an associated text label, the purpose of the form control may not be known by users. Add a <label> element to associate it with its form control. If the label isn''t visible, add an associated label, descriptive title attritubute to the form control, or reference the label using ''aria-labelledby''.','textarealabel');
INSERT INTO "messages" VALUES(14,'<noscript> Element Present','A <noscript> element is present. Content inside <noscript> is presented if JavaScript is disabled, but almost all screen reader users have JavaScript enabled. Be cautious in placing crucial or accessible content in <noscript>, because it''s often overlooked. Instead, ensure scripted content is accessible.','noscript');
INSERT INTO "messages" VALUES(15,'<header> Element Present','A <header> element identifies page introduction or navigation. It’s usually surrounding the site or page name, logo, navigation, or other header content. Make sure <header> surrounds page header content only, and add ARIA role=“banner” to ensure better accessibility support.','header');
COMMIT;
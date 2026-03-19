#!/usr/bin/env python3
"""
Script to add verified high-confidence data to learning cache.
This data will be used as golden references for future scraping.
"""

import json
import os
from datetime import datetime

LEARNING_CACHE_FILE = "learning_cache.json"

# Verified data from manual research - format: domain, first_name, last_name, company_name, address
VERIFIED_DATA = """
familiestvw.co.uk	Lesley	Chambers	Families Thames Valley West	
qsassociates.co.uk	Mark	Howe	QS Associates Ltd	QS Associates Ltd, Liberty House, Greenham Business Park, Newbury, RG19 6HS
pahirenorwich.co.uk	Timothy	Cargill	P A HIRE LIMITED	32 Low Bungay Road, Loddon, Norwich, England, NR14 6JW.
sus-tec.com				
labmotive.com	Kyle	McDuffie	CSols Laboratory Informatics Software and Services.	CSols Ltd. The Heath, Runcorn, Cheshire, WA7 4QX, UK
selectproperty.com	Adam	Price	Select Property Group Limited	Horseshoe Farm, Elkington Way, Alderley Edge. SK9 7GU
burohappold.com	Oliver	Plunkett	Buro Happold Limited	Camden Mill, Lower Bristol Road, Bath, BA2 3DQ, United Kingdom.
campaignworks.co.uk	Rob	Conway	THE CAMPAIGN WORKS LIMITED	Croft Chambers, 11 Bancroft, Hitchin, Hertfordshire, SG5 1JQ
kaleidovision.co.uk	Andy	Pitman	Kaleidovision Limited	Brickendonbury, Brickendon Lane, Hertford, Hertfordshire, SG13 8NP, United Kingdom
wedohr.co.uk	Karam	Fadloun	We Do HR Limited	1 Leith Road, Darlington, County Durham, DL3 8BE
resonatetesting.com	Tom	Mallon	Resonate Testing Ltd	Unit 1, Bridge Technology Park, Carnagat Lane, Chancellors Road, Newry, Co. Down, United Kingdom, BT35 8XF
artisanoption.co.uk	Peter	Foster	Art is an Option Limited	Alloa Business Centre, Office 72, Alloa, FK10 3SA, United Kingdom
questsolutionsltd.co.uk	Simon	Henry	Quest Solutions (UK) Ltd.	Unit 8 Millersdale Close, Euroway Trading Estate, Bradford, West Yorkshire, England, BD4 6RX
warriordoors.co.uk	Brett	Barratt	Warrior Doors Ltd.	Unit 4, Kings Road Industrial Estate Kings Road, Tyseley, Birmingham, West Midlands, B11 2AX.
fgsplant.co.uk	Trevor	Heathcote	F.G.S. PLANT LIMITED	Ferry House, New Hythe Lane, Aylesford, Kent, ME20 7PA
specialistsecurityco.com	Rachel	Fleri	Specialist Security Co Ltd	Suite B, First Floor Pod 1, Capital Shopping Park, Leckwith Road, Cardiff, Wales, CF11 8EG
britishblockassociation.org	Naseem	Naqvi	The British Blockchain Association	Kemp House, 152–160 City Road, London, EC1V 2NX, UK
smithsconcrete.co.uk	Gordon	Napier	Smiths Concrete Limited	Southam Road, Banbury, Oxfordshire OX16 2RR
exchangeresidential.com	Eve	Brown	Exchange Residential Limited	Nelson House, the Fleming Burdon Terrace, Jesmond, Newcastle upon Tyne, NE2 3AE
iceblue.co.uk	Jennifer	Long	ICEBLUE MARKETING AND DESIGN LIMITED	6 Church Street, Kidderminster, Worcestershire, DY10 2AD
grizzlytools.co.uk	Danny	Strollo	GRIZZLY TOOLS LIMITED	44 Elwell Street, West Bromwich, England, B70 0DN
oriensaviation.com	Edwin	Brenninkmeyer	Oriens Aviation Limited	Building 170, Churchill Way, London Biggin Hill Airport, Westerham, Kent, TN16 3BN, United Kingdom
globalheattransfer.co.uk	Clive	Jones	GLOBAL HEAT TRANSFER LIMITED	Cold Meece Estate, Cold Meece, Swynnerton, Stone, Staffordshire, ST15 0SP
mint-publishing.co.uk	Tom	Williams	Mint Publishing Limited	Unit 9 Cronin Courtyard, Weldon South Industrial Estate, Corby, Northamptonshire, NN18 8AG
purplemedia.co.uk	Joe	Kennard	Purple Media Ltd	1 Chapel Place, Northampton, Northamptonshire, NN1 4AQ
lives.org.uk	Nikki	Cooke	Lincolnshire Integrated Voluntary Emergency Service	LIVES Headquarters, Units 5-8 Birch Court, Boston Road Industrial Estate, Horncastle, Lincolnshire, LN9 6SB
officeoutlet.com	Chris	Yates	Office Outlet	Hampden Court, Kingsmead Business Park, High Wycombe, Buckinghamshire, HP11 1JU.
kenkamara.com	Ken	Kamara	Ken Kamara	3 Fowler House, South Grove, London, United Kingdom, N15 5QJ
keyplaneng.co.uk	Archie	Jefferies	KEYPLAN ENGINEERING LIMITED	64-766 Fishponds Road, Bristol, BS16 3UA
pcs-instruments.com	Steven	Horder	PCS Instruments Limited	78 Stanley Gardens, Acton, London, W3 7SZ, United Kingdom
macontrols.com	Jack	Morris	MAControls Limited	9 Enterprise Way, Cheltenham Trade Park, Cheltenham, GL51 8LZ, United Kingdom
kortec.co.uk	Carl	Groombridge	Kortec Ltd	Zenith Point, Belmore Way, Westside Park, Derby, Derbyshire, DE21 7AZ, England
firerecords.com	James	Nicholls	firerecords.com	4 Tyssen Street, Dalston, London, E8 2FJ, UK
cotswoldgrey.com	Simon	Jeffrey	Cotswold Grey Ltd	The Old Ironmongers, High Street, Moreton-in-Marsh, Gloucestershire, GL56 0AD, United Kingdom
globaltefl.uk.com	Harold	Bratovich	Global Language Training Ltd	20-22 Wenlock Road, London, N1 7GU, England
mesh-global.com	Barry	Canfield	Mesh Global Ltd	Mesh House, Brent Avenue, Montrose, DD10 9PB, United Kingdom
premier-office-supplies.co.uk	Mike	Penson	Premier Office Supplies Ltd	Unit 1, Marcus Close, Reading, Berkshire, RG30 4EA
dragonadvisory.com	Jonathan	Griffin	Dragon Advisory Limited	58 Grosvenor Street, London, W1K 4
hertalis.com	Gary	Colister	Hertalis Limited	86-90 Paul St, London, EC2A 4NE, UK
fsprops.co.uk	Iyas	Musa	First Step Property Maintenance	1-3 Coventry House, Ilford, Essex, IG1 4QR, United Kingdom
alarmsupply.com.sg	Thomas	Tan	Alarm Supply Pte Ltd	63 Jalan Pemimpin, #03-07 Pemimpin Industrial Building, Singapore 577219
rba-architects.co.uk	Robert	Benn	RBA Architects Limited	46 Wimborne Road, Southsea, Hampshire, PO4 8DE, United Kingdom
qvoice.co.uk	Nicola	Richardson	QVOICE LIMITED	Foresters Hall, 25-27 Westow Street, Crystal Palace, London, SE19 3RY, United Kingdom
theslice.com				
bletsoes.co.uk	David	Bletsoe-Brown	Henry H Bletsoe and Son LLP	Oakleigh House, 28 High Street, Thrapston, Kettering, Northamptonshire, NN14 4LJ
spartansafety.co.uk	Arvind	Maniar	SPARTAN SAFETY LIMITED	Unit 10, Stadium Business Park, Castle Road, Sittingbourne, Kent, ME10 3BG
thethirstalternative.co.uk	Christian	Daniels	The Thirst Alternative Limited	186 St Mary Street, Latchford, Warrington, Cheshire, WA4 1EL
d-zinefurniture.co.uk	Betsy	Vickery	Dzine Furnishing Solutions Ltd	D-Zine House, Severn Road, Stourport-on-Severn, Worcestershire, DY13 9EZ, UK
thompsons-feeds.co.uk	Colin	Bailey	William Thompson (York) Limited	Jubilee Mill, Murton Lane, York, North Yorkshire, YO19 5UT, United Kingdom
henrygallacher.co.uk	Alessandro	Lala	Henry Gallacher Limited	Jay Avenue, Teesside Industrial Estate, Stockton-on-Tees, TS17 9LN, United Kingdom
hillfoot.com	Craig	James	Hillfoot Steel Limited	Herries Road, Sheffield, South Yorkshire, S6 1HP, United Kingdom
digimagic.com.sg	Donald	Lim	Digimagic Communications Pte Ltd	176 Orchard Road, #05-05 The Centrepoint, Singapore 238843
ormdigital.com	Jim	Hartshorne	Paragon Customer Communications	16-18 Finsbury Circus, London, EC2M 7EB, United Kingdom.
juveaaesthetics.com	Faizeen	Zavahir	Juvea Aesthetics	1 Harley St, London, W1G 9QD, United Kingdom.
tinwaredirect.com	Guy	Grumbridge	Tinware Direct Limited	The Granary Crowhill Farm, Ravensden Road, Wilden, Bedford, Bedfordshire, MK44 2QS, United Kingdom
porterhouseinsights.com	David	Eatwell	Porterhouse Insights Limited	4 Windsor Square, Silver Street, Reading, Berkshire, United Kingdom, RG1 2TH
hallidayreeves.com	Mark	Reeves	Halliday Reeves	Boho Zero, 21 Gosford Street, Middlesbrough, TS2 1BB
lioneng.com	Geoff	Kimber-Smith	LION ENGINEERING	Gapton Hall Road, Gapton Hall Industrial Estate, Great Yarmouth, Norfolk NR31 0NL, United Kingdom
little-mansions.co.uk	Rachel	Johnson	Little Mansions Ltd	8 Eastgate Street, Stafford, England, ST16 2NQ
wearebrew.co.uk	Matthew	Bowell	Brew	The STEAMhouse, Cardigan Street, Birmingham, United Kingdom, B4 7RE.
sciaky.co.uk	Louis	Kunzig	Sciaky Electric Welding Machines Limited.	The Oak House, Cressex Business Park, Coronation Road, High Wycombe, Buckinghamshire, England, HP12 3RP
energyflo.co.uk	Alessio	Teoli	ENERGYFLO LTD	Jubilee House, 3 The Drive, Great Warley, Brentwood, England, CM13 3FR
granvilleecopark.co.uk	David	McKee	Granville Ecopark Limited	Granville Ecopark, Granville Industrial Estate, Dungannon, Northern Ireland, BT70 1NJ.
premierjobsuk.com	Gary	Venner	Premier Jobs UK Limited	Unit 6, Fourbrooks Business Park, Stanier Road, Calne, Wiltshire, SN11 9PP.
dockerills.co.uk	Malcolm	Dockerill	DOCKERILLS (BRIGHTON) LIMITED	15 West Street, Brighton, England, BN1 2RL
trslegalcosts.co.uk	Tim	Russell-Smith	TRS LEGAL COSTS LIMITED	Unit 5 Singleton Court Business Centre, Wonastow Road Industrial Estate (West), Monmouth, Gwent, NP25 5JA
reichmannproperties.com	Barry	Reichmann	Reichmann Properties PLC	Cavendish House, 369 Burnt Oak Broadway, Edgware, England, HA8 5AW
conceptoils.co.uk	Cameron	Alden	CONCEPT OILS LIMITED	18 Drome Road, Deeside, Clwyd, CH5 2NY
glazeandsave.co.uk	Tanya	Ewing	GLAZE AND SAVE LIMITED	68 Hay Street, Perth, PH1 5HP
hb-bearings.com	Graham	Hirst	HB Bearings Limited	Riverside Works, Honley, Holmfirth, Huddersfield, HD9 6PQ, United Kingdom
asurafin.com	David	Waddington	Asura Financial Technologies Ltd.	Royal Exchange, Panmure Street, Dundee, Scotland, DD1 1DU
hdc-uk.com	James	Darby	hdc Design and Print Solutions	Unit 2 Maritime Court, 8 Cartside Avenue, Inchinnan Business Park, Glasgow, PA4 9RX
residebath.co.uk	Ben	Bower	RESIDE BATH LIMITED	24 Barton Street, Bath, BA1 1HG
bridgevalleybeverages.co.uk	Bernard	Devenish	Bridge Valley Group	1 Block B Duffryn Park, Alder Avenue, Hengoed, Mid Glamorgan, CF82 7TW, United Kingdom.
vantagecomputing.co.uk	Tony	Milford	Vantage Computing Limited	1st Floor Meadow Barn, Fairclough Hall Farm, Halls Green, Herts, SG4 7DP
advancedphysiotherapy.co.uk	Muhammad	Chishti	Advanced Physiotherapy Ltd.	Unit 3 Sevenoaks Enterprise Centre, Bat & Ball Road, SEVENOAKS, TN14 5LJ
stoneseed.co.uk	Jamie	Buttle	Stoneseed Limited	3 Innovate Mews, Lake View Drive, Sherwood Business Park, Nottingham, NG15 0EA, United Kingdom
medkitchen.co.uk				
zpb-associates.com	Zoe	Bedford	ZPB Associates	C/o White Hart Associates LLP, 2nd Floor, Nucleus House, 2 Lower Mortlake Road, Richmond, TW9 2JA
lionspeciality.co.uk	Mark	Osborne	Lions Speciality Foods Limited	9 Sholto Crescent, Righead Industrial Estate, Bellshill, Lanarkshire, Scotland, ML4 3LX
pin-itpastry.com	Ceri	Jones	Pin-It Pastry Ltd	Abergarw Industrial Estate, Brynmenyn, Bridgend, Wales, CF32 9LW
bridgewaterwindscreens.co.uk	Andrew	Sampson	BRIDGEWATER WINDSCREENS LIMITED	Unit 11, Stonehill Business Centre, Stonehill Road, Farnworth, Bolton, BL4 9TP
betteryou.com	Andrew	Thomas	BetterYou Ltd	Unit 24 Shortwood Court, Shortwood Business Park, Dearne Valley Parkway, Barnsley, S74 9LH
chapplins.co.uk	John	Belstone	CHAPPLINS ESTATE AGENTS (FAREHAM) LIMITED	9 - 11 West Street, Fareham, PO16 0BG, United Kingdom
flowtechinternational.co.uk				
infraguard.co.uk	Jack	Longmate	INFRAGUARD LIMITED	20 Lisburn Road, Saintfield, Ballynahinch, Northern Ireland, BT24 7AL
rhf.co.uk	William	Kelly	Roy Hopwood (Fasteners) Ltd.	Units 1 & 2, Martel Court, S Park Business Park, Stockport, Cheshire, England, SK1 2AF
platypusresearch.com	Jo	Cliff	Platypus Research Limited	Roseleigh, Headlands Road, Ossett, England, WF5 8HY
riverhomes.co.uk	Russell	Day	World Waterside Ltd	28 Thames Road, Chiswick, London, W4 3RJ
jellyfishlivewire.co.uk	Graham	Lycett	JELLYFISH LIVEWIRE LIMITED.	Oculis House Suite 13, Eddystone Road, Southampton, Hampshire, SO40 3SA, United Kingdom
powellelectrical.co.uk	Elizabeth	Clarke	JPE Electrical Services Limited	Crestacre Farm, Walsall Wood, West Midlands, WS9 9DL
breathedigital.co				
harrisonfm.co.uk	Russell	Harrison	Harrison Facilities Management Group Ltd	32 Friar Gate, Derby, United Kingdom, DE1 1BX.
mesnw.co.uk	Ged	Walker	MES (NW) LIMITED	749a Ormskirk Road, Wigan, England, WN5 8AT.
apexhousingsolutions.co.uk	Vatche	Cherchian	APEX HOUSING SOLUTIONS LTD	Unit 3.10 Grand Union Studios, 332 Ladbroke Grove, London, England, W10 5AD
hkjewellery.co.uk	Rebecca	Howarth	Harriet Kelsall Jewellery Design Ltd.	North Barn, Fairclough Hall Farm, Halls Green, Herts SG4 7DP, UK
aldrichgroup.co.uk	Oliver	Tookman	ALDRICH GROUP LIMITED.	Unit 10 Hillside Road, Bury St. Edmunds, England, IP32 7EA.
whitesbakery.co.uk	David	White	WHITE'S BAKERY LIMITED	Worsbrough Bridge, United Kingdom, S70 5AF
hungrydonkey.co.uk	Markos	Tsimikalis	HUNGRY DONKEY LTD LIMITED.	76 Stewarts Road, Nine Elms, London, England, SW8 4D
tedbartinkerhire.co.uk	John	Gunby	Tedbar Tinker Hire Limited	96 Holywell Road, Sheffield, United Kingdom, S4 8AS
cofesuffolk.org	Joanne	Grenfell	Diocese of St Edmundsbury and Ipswich	St Edmundsbury and Ipswich Diocese, 4 Cutler Street, Ipswich, IP1 1UQ
tallgroup.co.uk	Martin	Ruda	The TALL Group of Companies	Unit 2, Pembroke Court, Manor Park, Runcorn, Cheshire, WA7 1TJ, United Kingdom
riftaccounting.com	Dermot	Kennedy	Rift Accounting Ltd	160 Eureka Park, Upper Pemberton, Kennington, Ashford, Kent, England, TN25 4AZ
beehiveresearch.co.uk	Paul	Kavanagh	Beehive Research Ltd	Amherst House, 22 London Road, Riverhead, Sevenoaks, United Kingdom, TN13 2BT
amandahowardassociates.co.uk	Amanda	Howard	Amanda Howard Associates Limited	2 Percy Street, London, England, W1T 1DD
the-omj.com	Ian	Moore	The Oil Market Journal	1A Blackstick Road Killyhevlin Enniskillen Co Fermanagh BT74 4EB.
monofil.co.uk	Markus	Fritzsche	Monofil Limited	139 College Road, Birmingham, B13 9LJ, United Kingdom
wattsgallery.org.uk	Madeline	Henderson	Watts Gallery - Artists' Village	Down Ln, Compton, Guildford, Surrey, GU3 1DQ, United Kingdom
scottses.com	Gordon	Nixon	Scotts Electrical Services Ltd	Unit C2, 20 Heron Road, Belfast Harbour Estate, Belfast, Northern Ireland, BT3 9LE
beatuscartons.co.uk	Clive	Stinchcombe	Beatus Cartons (Jacob Beatus Limited)	North Road, Porth, Rhondda Cynon Taff, CF39 9SP, United Kingdom
clarkeprint.co.uk	Nigel	Clarke	Clarkeprint Limited	45-47 Stour Street, Birmingham, West Midlands, B18 7AJ
klmproperty.co.uk	Manish	Somani	KLM PROPERTY LIMITED	309 Hoe Street, London, England, E17 9BG
mcomputer.com	Roony	Mobarik	M COMPUTER TECHNOLOGIES	Unit 307, 11 Harrowby Street, London, W1H 5PQ
classicbuildinggroup.co.uk	Mark	Eckersley	Classic Building Group	Albert Street Works, Albert Street, Manchester, M43 7BA
margotrestaurant.com	Paulo	de-Tarso	Margot restaurant	45 Great Queen Street, Covent Garden, London WC2B 5AA, GB
clarkesrestaurant.co.uk	Sally	Clarke	SALLY CLARKE RESTAURANT LIMITED	124 Kensington Church Street, London, W8 4BH
beanstalkmarketing.co.uk	Phil	Swanson	Beanstalk Marketing Services Ltd	4th Floor, Dencora Court, Tylers Avenue, Southend-On-Sea, Essex, SS1 2BB
etavoni.com	Simon	Hurd	Etavoni Limited	Unit A Wellsway Works, Wells Road, Radstock, Banes, BA3 3RZ.
colson.co.uk	Andrew	Taylor	Colson X-Cel Ltd	Unit 3a Brindley Way Rotherham S60 5FS
pcmseng.co.uk	Andy	Chater	PCMS Eng Group	British Engineering Services Unit 718 Eddington Way, Birchwood Park, Warrington, United Kingdom, WA3 6BA
sonitechindia.com				
southbynorth.co.uk	Martin	Northern	South by North Ltd	23-24 The Oakwood Centre, Downley Road, Havant, Hampshire, PO9 2N
torrscientific.co.uk	David	Bates	Torr Scientific Limited	Unit 11 Pebsham Rural Business Centre Pebsham Lane Bexhill-on-Sea East Sussex TN40 2RZ United Kingdom
aerospacebristol.org	Sally	Cordwell	Aerospace Bristol	The Clock Tower, 5 Farleigh Court, Old Weston Road, Flax Bourton, Bristol BS48 1UR
carlisleunited.co.uk	Tom	Piatak	Carlisle United Football Club	Brunton Park, Warwick Road, Carlisle, CA1 1LL, England, United Kingdom
thedunegroup.com	Nigel	Darwin	The Dune Group Limited	The White Building 4th Floor, 11 Evesham Street, London, England, W11 4AJ
icecreamrecords.co.uk	Andreas	Symeon	Ice Cream Records Limited	1st Floor Woodgate Studios, 2-8 Games Road, Cockfosters, Hertfordshire, United Kingdom, EN4 9HN
corecomconsulting.co.uk	Jonathan	Sanderson	Corecom Consulting Ltd	Yorkshire Hub, Greek Street, Leeds, LS1 5SH
pennyandsinclair.co.uk	James	Penny	Penny & Sinclair Ltd	Unit 2 Mayfield House, Banbury Road, Summertown, Oxford, OX2 7DE
sgcsecurityservices.co.uk	Paul	Macarthur	SGC Security Services	Unit 2, Cherry Tree Farm, Blackmore End Road, Halstead, Essex, CO9 3LZ, United Kingdom
colan-uk.net	Mike	Hancox	Colan Ltd	Unit 28 Hurlbutt Road, Heathcote Ind Estate, Warwick, CV34 6TD.
optimize.co.uk	Mike	Rogers	Optimize Search Marketing	20-22 Wenlock Road, London, N1 7GU
sportingedge.com	Jeremy	Snape	Sporting Edge Digital Limited	Innovation Centre Airfield Business Park, Wellington Way, Market Harborough, Leicestershire, LE16 7WB, United Kingdom
pendragonframes.com	Keith	Andrews	Pendragon Fine Art Frames Limited	Unit 10 Rangemoor Industrial Estate, Rangemoor Road, London, N15 4NG, England
sb7mobile.com	Jonathan	Brown	SB7 Mobile Ltd	2 Manor Farm Court Old Wolverton Road, Old Wolverton, Milton Keynes, England, MK12 5NN
eps-uk.co.uk	Brian	McKean	E.P.S. (UK) LIMITED	Units N & O, Freeth Street, Nottingham, Nottinghamshire, NG2 3GT
luvyababes.co.uk	David	Williams	Luvyababes Ltd	Okyloki LTD t/a Luvyababesx, 304, Victoria Centre, Nottingham, NG1 3QN,
quinntoolsgroup.co.uk	Matthew	Beverley	QUINN TOOLS AND FASTENERS LIMITED	159 Railway Terrace, Rugby, Warwickshire, CV21 3HQ, United Kingdom
lincolncityfoundation.co.uk	Martin	Hickerton	LINCOLN CITY FOUNDATION	LNER Stadium, Sincil Bank, Lincoln, England, LN5 8LD
fidelis-security.com	Eric	Moseman	Fidelis Cybersecurity	871 Marlborough Ave, Suite 100, Riverside, CA 92507, USA
braidlock.com	Barry	Cunningham	Braidlock Limited	Unit 5, Farrell Industrial Estate, Howley Lane, Warrington, United Kingdom, WA1 2PB
omega.nl				
stylefrogcreative.com	Matthew	Faulkner	STYLEFROG CREATIVE LTD	3 Paradise Avenue, Kettering, England, NN15 6LU
darwindidit.com	Ian	Todd	Darwin Press Limited	Unit B, Pier Road, Feltham, Middlesex, TW14 0TW, GB
drivermetrics.com	Nicholas	Rowley	DRIVERMETRICS LIMITED	No 1, The Cranfield Innovation Centre, Cranfield University Technology Park, Cranfield, Bedfordshire, England, MK43 0BT
lilouetloic.com	Malin	Wright	Lilou et Loïc Ltd	Chelsea Old Town Hall, Kings Road, London, England, SW3 5EZ
mccalls.co.uk	Iain	Hawthorne	McCalls Limited	15-17 Bridge Street, Aberdeen, Scotland, AB11 6JL
combined-knowledge.com	Brian	Brown	Combined Knowledge Ltd	2 The Terrace, Rugby Road, Lutterworth, Leicestershire, LE17 4BW, England, United Kingdom
mmsj.co.uk	Mick	Morton	MM Shopfitting & Joinery Ltd	24 West Street, Hucknall, Nottingham, NG15 7BY, GB
fingerprints.co.uk	Allan	Kerr	Fingerprints	Unit 3, Andrews Court, Andrews Way, Barrow-in-Furness, LA14 2UE.
clockspeed.co.uk	Mark	Johnston	ClockSpeed Marketing Ltd	180/186 Kings Cross Road London WC1X 9DE
amcorenewables.co.uk	Jordan	Johnson	Amco Renewables	Unit 8-9 Wheatley Hall Trade Park, Doncaster, South Yorkshire, DN2 4NH, United Kingdom
flowersbysuzanne.co.uk	Alison	Fowler	Flowers By Suzanne Limited	141 Moor Lane, North Hykeham, Lincoln, England, LN6 9AA.
adrocgroup.co.uk	Rhys	Evans	AdRoc Group	25 Old Broad St, London, Greater London, EC2N 1HN, United Kingdom.
tambeauty.com				
unitedguards.org				
stirlinganglianpharmaceuticals.com	Mark	Inker	Stirling Anglian Pharmaceuticals Ltd	Hillington Park Innovation Centre, 1 Ainslie Road, Hillington Park, Glasgow, G52 4RU, United Kingdom.
trwilliamson.co.uk	Amr	Sheibani	T&R Williamson Limited	The Paintworks, 36 Stonebridgegate, Ripon, North Yorkshire, HG4 1TP.
essexsecurity.co.uk	Andrew	Donoghue	Essex Security Services Ltd	154-156 Church Hill, Loughton, Essex, IG10 1LJ
artifax.net	Andy	Wheeler	Artifax Software Limited	5th Floor, 167-169 Great Portland Street, London, W1W 5PF, United Kingdom
brandsearchint.co.uk	Andrew	Wallington	Brand Search Limited	Dakota Way, Burscough, L40 8AF
totalsteelfabs.com	Mike	Lomax	Total Steelwork & Fabrications Ltd	Unit 3-5 Causeway Works, Palatine Industrial Estate, Causeway Avenue, Warrington, Cheshire, WA4 6AB, United Kingdom
blackrockpharma.com	Philip	Mcferran	Blackrock Pharmaceuticals Limited	The Old Barrel Store, Brewery Courtyard, Draymans Lane, Marlow, Buckinghamshire, SL7 2FF, United Kingdom
prestigeapartments.co.uk	Alexandra	Wood	Prestige Apartment Services Limited	43 Sudbury Heights Avenue, Middlesex, UB6 0ND, United Kingdom
pacificwestfoods.co.uk	Martin	Firegan	Pacific West Foods (UK) Ltd	3 Willowside Park, Canal Road, Trowbridge, Wiltshire, BA14 8RH
ithotdesk.com	Sohin	Raithatha	IT HOTDESK LTD	23 Abercrombie Court, Arnhall Business Park, Westhill, Aberdeen, Scotland, AB32 6FE
carouselshop.co.uk	Kate	Turvey	Shoppydays Ltd	Kallo Building, Units 1A-1C and 2A-2B, Coopers Place, Combe Lane, Wormley, Surrey, GU8 5SZ
savant-health.com	Abby	Smith	Savant Distribution Ltd	Quarry House, Clayton Wood Close, Leeds, LS16 6QE, United Kingdom
cbtclinics.co.uk	Antony	Brown	CBT Clinics	First Floor, West Wing, Holgate Park Drive, York YO26 4GN, England, United Kingdom
netready.biz	Scott	McLaren	Netready Limited	Phoenix Yard, Upper Brown Street, Leicester, LE1 5TE, United Kingdom
gaphomeimprovements.co.uk	Paul	Watts	GAP Home Improvements Ltd	Rear of Roxton Garden Centre, Bedford Road, Roxton, Bedford, MK44 3DY
isaconsortium.co.uk	Sarosh	Khan	ISA Consortium Ltd	206 New Road, Croxley Green, Rickmansworth, England, WD3 3HH
vani-t.com	Tania	Walsh	VANI-T Pty. Ltd	5 Kitawah St, Lonsdale, South Australia, 5160, Australia
toorakpackaging.co.uk	Richard	Hancock	Toorak Limited	Curo House, Greenbox, Westonhall Road, Stoke Prior, Bromsgrove, Worcestershire B60 4AL.
packagedsounds.com	Barry	Hurley	Packaged Sounds Group / Packaged Sounds Ltd	Unit 2, The Valley Centre, Gordon Road, High Wycombe, Buckinghamshire, HP13 6EQ, United Kingdom
explomould.co.uk	Kevin	Lawrence	Explomould Engineering Services Ltd	Mill Lane, Arlesey, Bedfordshire, SG15 6RF, United Kingdom
ashcommunications.com	Lynda	Heath	Ash Communications	133 Whitechapel High Street, London, United Kingdom, E1 7QA
hengoedcourt.co.uk	Desmond	Davies	Hengoed Court Care Home	5 Llys Felin Newydd, Phoenix Way, Enterprise Park, Swansea, West Glamorgan, SA7 9FG
painterbrothers.com	Zach	Tanner	Painter Brothers Limited	Painter Brothers, Holmer Road, Hereford, HR4 9SW, United Kingdom
interaction-ld.com	Katie	Scott	Interaction learning and development limited	The Mews Hounds Road, Chipping Sodbury, Bristol, BS37 6EE
radiocentre.org	Matt	Payton	RADIOCENTRE LIMITED	15 Alfred Place, London, WC1E 7EB.
cartwrighthands.com	Guy	Hands	Cartwright Hands	59 Coton Road, Nuneaton, Warwickshire, CV11 5TS
jentelpacking.co.uk	Terry	Loosley	Jentel Packing Ltd	1506 London Road, Leigh-On-Sea, England, SS9 2UR
cjconstructionltd.com	James	Payne	C.J. Construction (Surrey) Ltd	1-3 Wealdstone Road, Sutton, Surrey, SM3 9QN, United Kingdom
adyoung.com	Sam	McKay	A.D. Young Technical Services Limited	53 Fore Street, Ivybridge, Devon, PL21 9AE
lockfit.co.uk	Kevin	Russell	LOCKFIT LTD	12 Flint Avenue, Tatenhill, Burton-On-Trent, England, DE13 9GL
ospreymc.co.uk	Linzy	Schaller	Osprey Management Company	112 Mill Platt, Old Isleworth, Middlesex, TW7 6BZ.
mylocalbobby.co.uk	David	McKelvey	My Local Bobby Limited	Roding House, 2 Victoria Road, Buckhurst Hill, Essex, England, IG9 5ES.
maylan.com	Heather	Bresch	Maylan Engineering Ltd	Unit 7, Darwin Court, Trevithick Road, Corby, Northamptonshire, England, NN17 5XY
tiptoptoilets.co.uk	Matthew	Rees	Tip Top Toilets Limited	Fedw Hir, Llwydcoed, Aberdare, Wales, CF44 0DX
touchpanels.co.uk	Martin	Strange	Touch Panel Products Limited	Unit 3 Short Way, Thornbury Industrial Estate, Thornbury, Bristol, Gloucestershire, BS35 3UT, United Kingdom.
markjohnstonracing.com	Mark	Johnston	Johnston Racing Limited	Kingsley Park, Park Lane, Middleham, Leyburn, North Yorkshire, DL8 4QZ, England
progressivecare.co.uk	Mohammad	Ali	Progressive Care Limited	51 Attercliffe Common, Sheffield, South Yorkshire, S9 2AE, UK.
scottcables.com	Gary	Scott	Scott Cables Limited	Unit 7 Merlin Park, Airport Service Road, Portsmouth, Hampshire, PO3 5FU, UK.
onenation.co.uk	Pauline	Hanson	One Nation	2a Oxford Street, Batley, West Yorkshire, WF17 7PZ, UK
arts1.co.uk	Rebecca	Carrington	Arts1 School of Performance	1 Danbury Court, Linford Wood, Milton Keynes, MK14 6LR
onyxcomms.com	Anne	Griffin	Onyx Media and Communications	49 Greek Street, Soho, London, W1D 4EG
verulamwebdesign.co.uk	Nigel	Minchin	Verulam Web Design	47 Meadowcroft, St. Albans, Hertfordshire, AL1 1UF
sunrisesoftware.com	Dean	Coleman	Sunrise Software	5th Floor, 167-169 Great Portland St, London, W1W 5PF
sidekickpr.com	Charlotte	Dimond	Sidekick PR	The Quadrant, 99 Parkway Avenue, Sheffield, South Yorkshire, S9 4WG
frenchbrothers.co.uk	Christopher	French	French Brothers Ltd	The Runnymede Boathouse, Windsor Road, Old Windsor, Berkshire, SL4 2JL
lecsuk.co.uk	Dave	Cooper	LECS (UK) Ltd	Grosvenor Gardens, Terminal House, London, Greater London, SW1W 0AU
abcomm.co.uk	Katie	Macaulay	AB Comms Limited	173 College Road, Liverpool, England, L23 3AT
edwardwilliamsarchitects.com	Edward	Williams	Edward Williams Architects	Newcombe House, 45 Notting Hill Gate, W11 3LQ, UK
curvemotion.com	Tobias	Bayliss	Curve Motion	Lark Valley Business Park, Lamdin Road, Bury St Edmunds, Suffolk, IP32 6LJ
h-s-p.co.uk	Stephen	Hollis	Hydraulic System Products Ltd	3 Monckton Road Industrial Estate, Monckton Road, Wakefield, West Yorkshire, WF2 7AL.
norrsken.co.uk	Niklas	Adalberth	Norrsken Company Limited	Unit 9/10 Alpha Centre, Upton Road, Poole, Dorset, BH17 7AG.
adgenuk.com	Verity	Brown	Adgen Ltd	2 Chapel Court, 42 Holly Walk, Leamington Spa, Warwickshire, CV32 4YS, United Kingdom.
utilivista.com	Nigel	Williams	Utilivista Limited	Westfields, Thornton Road, South Kelsey, Market Rasen, Lincolnshire, LN7 6PS.
kb-2.co.uk	Timothy	Pattinson	KB2 Consulting Engineers Limited	Arclight House 3 Unity Street Bristol BS1 5HH
itiuk.com	Brendan	Fahy	Instruments to Industry Ltd	Euro Works, Hawksley Industrial Estate, Hawksley Street, Oldham, OL8 4PQ, United Kingdom
thecleverbaggers.co.uk	Darren	Davies	The Clever Baggers Ltd	5 Four Crosses Business Park, Llanymynech, Powys, Wales, SY22 6ST.
printwell.co.uk	Hussein	Ghor	Printwell UK Ltd	Windsor House, 26 Willow Lane, Mitcham, Surrey, CR4 4NA.
conservancy.co.uk	Matt	Briers	Chichester Harbour Conservancy	The Harbour Office, Itchenor, Chichester, West Sussex PO20 7AW.
primarypcsolutions.co.uk	Philip	Williams	Primary P C Solutions Limited	13 Church Street, Helston, Cornwall, England, TR13 8TD.
boxlockengineering.com	Geoffrey	Marshall	Boxlock Engineering Limited	Unit 3, Roman Way Bath Business Park, Peasedown St. John, Bath, England, BA2 8SG.
larkuk.co.uk	Carlos	Smith	L.A.R.K Legal Limited	Daws House, 33-35 Daws Lane, London, NW7 4SD.
thesalgroup.com		S A L GROUP LIMITED	Ground Floor Progress House, 41 Progress Road, Eastwood, Leigh On Sea, Essex, England, SS9 5PR
conductor.london	Charlotte	Constance	Conductor London	The Conductor, 1 Fleet Place, Farringdon, London, EC4M 7RA.
quartzfabrications.co.uk	Matthew	Singleton	Quartz Fabrications Ltd	6 Abbots Quay, Monks Ferry, Birkenhead, Wirral, England, CH41 5LH
c-capture.co.uk	Tom	White	C-Capture Limited	Windsor House, Cornwall Road, Harrogate, North Yorkshire, England, HG1 2PW.
schwank.co.uk	Paul	Wilkins	Schwank Limited	Unit D2, Armthorpe Enterprise Park, Rands Lane, Armthorpe, Doncaster, South Yorkshire, England, DN3 3DY.
spikeglobal.com	Jeremy	Heath-Smith	Spike Global Limited	Waverley House, 115 - 119 Holdenhurst Road, Bournemouth, Dorset, England, BH8 8DY.
dints.com	Geoffrey	Mowbray	Dints International Ltd	Jamieson Stone, 2nd Floor Windsor House, 40-41 Great Castle Street, London, England, W1W 8LU.
kentofficespace.co.uk	Paul	Thomas	kent office space	Conqueror Court, Sittingbourne, Kent, ME10 5BH.
championcontractors.co.uk	Jim	McMeekin	Champion Contract Services Ltd	1 Worsley Court, High Street, Worsley, Manchester, M28 3NJ.
consec-risk.com	Gareth	Burgum	Consec Risk Management Ltd	Unit E10a - The Knoll Business Centre, 325-327 Old Shoreham Road, Hove, England, BN3 7GS.
lel.uk.com	Niki	Robinson	LEL Nuclear Ltd	Unit 1 Joseph Noble Road, Lillyhall, Workington, Cumbria, United Kingdom, CA14 4JX.
lvmedia.co.uk	Paul	Bell	LV Media Web Design Limited	G7 Europa Business Park, 67 Bird Hall Lane, Stockport, Greater Manchester, England, SK3 0XA.
securetoolsatheight.com		Secure Tools For Working At Height Limited	Mackenzie Goldberg Johnson Limited Scope House, Weston Road, Crewe, CW1 6DD
stpetersbrighton.org	Dan	Millest	St Peter's Church Brighton	York Place, Brighton, East Sussex, BN1 4GU, United Kingdom
smartbags.co.uk	Matt	Lewis	Smartbags Limited	JMH House, 481 Green Lanes, London, England, N13 4BS
lexiconfiresystems.co.uk	Kevin	Goggins	Lexicon Fire Systems Limited	Unit 3 Saltmore Farm, New Inn Road, Baldock, Hertfordshire, SG7 5EZ
linealservices.com	Kent	Teague	Lineal Limited	75-185 Gray's Inn Road, 3F-300, London, Camden, WC1X 8UE
altransliquids.co.uk	Jonathan	Dembrey	Altrans Liquids Limited	Sheephouse Farm, Uley Road, Nr. Dursley, Gloucestershire, GL11 5AD
macmarney.co.uk	Dawn	Marney	MAC MARNEY REFRIGERATION AND AIR CONDITIONING LIMITED	The Old Forge, Stone Street, Crowfield, Suffolk, IP6 9SZ
assured-systems.com	James	Priest	ASSURED SYSTEMS (UK) LTD	Unit A5 Douglas Park, Opal Way, Stone Business Park, Stone, Staffordshire, ST15 0YJ
fosterlomas.com	Will	Foster	FOSTER LOMAS ARCHITECTS LIMITED	6 Bluelion Place, 237 Long Lane, London, SE1 4PU
smartax.co.uk	Sajjad	Rajan	SMARTAX LIMITED	8 Station Road, Harrow, Middlesex, HA2 7SE
robust-uk.com	Ian	Johns	ROBUST UK LIMITED	Lymedale Business Park, Coaldale Road, Newcastle-Under-Lyme, Staffordshire, ST5 9QX
witpress.com	Carlos	Brebbia	WIT Press Limited	Ashurst Lodge, Ashurst, Southampton, Hampshire, SO40 7AA, UK
claudehooper.co.uk	Jonathon	Hooper	Claude Hooper Limited	4 Mount Ephraim Road, Tunbridge Wells, Kent, TN1 1EE, UK
ansaelevators.co.uk	Alex	Greenhalgh	ANSA Elevators Limited	21 Broadgate, Broadway Business Park, Chadderton, Lancashire, OL9 9XA, UK
freshgs.com	Jeff	Todd	Fresh Graphic Solutions Limited	4 The Workshop, Tolworth Close, Surbiton, Surrey, KT6 7EW, UK
skarbekassociates.com	Toni	Marshall	Skarbek Associates Limited	12-14 Upper Marlborough Road, St Albans, Hertfordshire, AL1 3UU, UK.
peligoni.com		Peligoni Booking Services Limited	Unit 5, The Bull Pen, Churchill Heath Farm, Kingham, Chipping Norton, Oxfordshire, OX7 6UJ, UK
broadcastradio.com	Liam	Burke	Broadcast Radio Limited	1-2 Maritime House, Maritime Business Park, Livingstone Road, Hessle, HU13 0EG, UK
ptmdesign.co.uk	Adam	McGrory	P T M Design Limited	Unit B2, Sovereign Park Industrial Estate, Lathkill Street, Market Harborough, Leicestershire, LE16 9EG, UK
deeter.co.uk	Joseph	Whiteaker	Deeter Electronics Ltd	Deeter House, Valley Road, Hughenden Valley, High Wycombe, Bucks, HP14 4LW, UK
connectcs.com		Connect CS Limited	Connect, 5th Floor, 90 Fenchurch Street, London, EC3M 4BY
vdcgroup.com	Ashwin	Bedi	VDC Group Limited	4th Floor 100 Fenchurch Street, London, England, EC3M 5JD
southernheadfishing.com		Southern Head Fishing Co. Limited	Net Shop 6, Fishing Station, Royal Parade, Eastbourne, East Sussex, England, BN22 7LD
multitask-computing.co.uk	Stuart	Cooper	Multitask Computing Limited	Black Barn, Valley Road, Fawkham, Kent, United Kingdom, DA3 8LY
juniperwealth.co.uk	Jon	Doyle	Juniper Wealth Management Limited	The Old Dock House, 90 Watery Lane, Ashton-On-Ribble, Preston, England, PR2 1AU
fantasticmedia.co.uk	Andy	Hobson	Fantastic Media UK Ltd	8-16 Dock Street, Leeds, England, LS10 1LX
ensyst.com.sg		EN-SYST EQUIPMENT & SERVICES PTE LTD	48 Tuas Basin Link, Singapore 638778
fourwavecommunications.com	Jonathan	Lee	FourWave Communications and Consultancy	EclectiQ House, Armistead Way, Cranage, Cheshire, CW4 8FE, UK
alphasafety.co.uk	Paul	Jones	Alpha Safety Training Ltd	Suite 9a Henley House, Queensway, Fforestfach, Swansea, SA5 4DJ, UK
ptfeflex.uk.com	Terence	Chadwick	PTFEFLEX LTD	10-11 Charterhouse Square, London, England, EC1M 6EE
parrott.co.uk	Stephen	Parrott	Parrott & Parrott Accountants	Unit 5F, South Hams Business Park, Devon, TQ7 3QH
noiseairconsultants.co.uk	Matt	Malone	NoiseAir Limited (formerly NoiseAir Ltd)	The Counting House, High Street, Lutterworth, Leicestershire, LE17 4AY
buxtonmcnulty.co.uk	Terence	McNulty	Buxton & McNulty Mechanical Services Limited	Unit 28, Alder Close, Horizons Business Centre, Veridion Park, Erith, Kent, DA18 4AJ
ludwellstores.co.uk	Phil	James	Ludwell Village Stores and Post Office	Post Office Glenmoray, Ludwell, Shaftesbury, Dorset, SP7 9ND
whitecommercial.co.uk	Chris	White	White Commercial Surveyors Ltd	Charter Court, 49 Castle Street, Banbury, Oxfordshire, OX16 5NU
ppuk.com	Greg	Harding	Precision Products (UK) Ltd	Unit 1, Cobnar Wood Close, Chesterfield Trading Estate, Chesterfield, S41 9RQ
buildsolar.co.uk	Hasan	Baig	Build Solar	University of Exeter, Northwick House, Exeter, EX4 4QF
euromedlimited.com	Chibuike	Agaruwa	Euromed Limited	16T Ramat Crescent, Ogudu GRA, Lagos, Nigeria
bournecoast.co.uk	Des	Simmons	Bournecoast Ltd	26 Southbourne Grove, Southbourne, Bournemouth, Dorset, BH6 3RA
ltg-ltd.com	Robert	Wilson	Lightning Transport Group Ltd	Lightning Transport Group Ltd, 5 Foxoak Park, Common Road, Dunnington, York, YO19 5RZ
ilm2amal.org	Ahmad	Malas	Ilm2Amal	17-19 High Street, Hounslow, Middlesex, TW3 1RH
blakefire-security.co.uk	Ian	Blake	Blake Fire & Security Systems	403 Sutton Road, Southend-on-Sea, Essex, SS2 5PQ
discountedcleaningsupplies.co.uk	David	Simcox	Discounted Cleaning Supplies Ltd	135 - 139 West Street, Crewe, Cheshire, CW1 3HH
furniture123.co.uk	Nick	Glynne	Furniture123	Unit J6, Lowfields Business Park, Elland, West Yorkshire, HX5 9DA
finecast.co.uk	Chris	Heatley	Fine-Cast Foundry Limited	1 Lineside Way, Littlehampton, West Sussex, BN17 7EH
ics.uk.net	Ismail	Bhamji	Industrial Control Systems Limited	Unit 6 Traso Business Park, Callywhite Lane, Dronfield, Derbyshire, S18 2XR
lofbergs.co.uk	Anders	Fredriksson	Löfbergs UK	5 Green Mews, Bevenden Street, London, N1 6AS
vanguardiaconsulting.co.uk	Jim	Griffiths	Vanguardia	21 Station Road, West Byfleet, Surrey, KT14 6DR
advancedpaints.co.uk	Danny	O'rourke	Advanced Paint Solutions Limited	Unit 1 Barley Close Farm, New Road, Bromham, SN15 2JA
midlandradiolinks.com	Nicholas	Baker	Midland Radio Links Limited	18 Boultbee Business Park, Nechells Place, Birmingham, B7 5AR
argentdesign.co.uk	Nicola	Fontanella	Argent Design Limited	134 Buckingham Palace Road, London, SW1W
systematicsecurity.co.uk	Afzal	Mohammed	Systematic Security Ltd.	Premier House, 309 Ballards Lane, London, N12 8LY, United Kingdom.
wpnchameleon.co.uk	John	Watson	WPN Chameleon Limited	Eoffice 1, Richmond Mews, Soho, London, W1D 3DA, United Kingdom.
civicareeast.co.uk	Jackie	Casey	Civicare East Ltd.	Lakeview House, 4 Woodbrook Crescent, Billericay, CM12 0EQ, United Kingdom.
donutsafetysystems.com	Claire	Williams	Donut International Limited	Unit 6, 1A International Avenue, Dyce, Aberdeen, AB21 0BH, United Kingdom.
islayohara.co.uk	Islay	O'Hara	Islay O'Hara (Public Relations Consultant).	Langton Road, Tunbridge Wells, Kent, United Kingdom.
jamesaturner.co.uk	Gary	Hyde	James A Turner Limited.	54 St Andrews Street, Hertford, Hertfordshire, SG14 1JA, United Kingdom.
xpeditegoc.com	Dean	Moss	Xpedite Group of Companies Ltd.	The Granary, Southstoke Lane, Southstoke, Bath, BA2 7PQ, United Kingdom.
kfkosher.org	Rabbi	Zimmerman	KF Kosher	65 Watford Way, London, NW4 3AQ, United Kingdom.
mellishengineering.co.uk	Alistair	Burns	Mellish Engineering Services Limited.	Saville House, Middlemore Lane West, Aldridge, Walsall, WS9 8BG, United Kingdom
mr-homes.co.uk	Mike	Roach	Mr Homes Estate Agents Ltd.	Homes House, 253 Cowbridge Road West, Cardiff, CF5 5TD, United Kingdom.
acuitytraining.co.uk	Ben	Richardson	Acuity Training Limited	Surrey Technology Centre, 40 Occam Road, Guildford, Surrey, GU2 7YG
devereintellica.com	Simon	Kidd	De Vere Intellica Limited	7, Bell Yard, London, WC2A 2JR, England
sangersaah.co.uk	Luc	Sangers	Sangers (Northern Ireland) Limited	20, Wenlock Road, London, N1 7GU, England
themayfairprintingco.com	Allison	Bourdice	The Mayfair Printing Co.	13-14 Queen Street, London, W1J 5PS
bartechturbos.com	Harry	Morgan	Maxitech Limited	Lawley House, Butt Road, Colchester, Essex, CO3 3DG
york-it-services.co.uk	Khadijah	Radzi	York IT Services (UK) Ltd	267 Melrosegate, York, YO10 3ST
parkcitylondon.co.uk	Caroline	Cox	Parkcity Limited	18-30 Lexham Gardens, Kensington, London, W8 5JE
bpmsltd.co.uk	Simon	Langley	Bespoke Property Management Services Ltd (BPMS Ltd)	6 Alexandra Road, Colchester, Essex, CO3 3DB
practicemanagersuk.org	Muhammad	Othman	Practice Managers Association (PMA)	PMA House, The Old Post Office, 1 Macclesfield Road, Alderley Edge, Cheshire, SK9 7BQ
holdsworth-foods.co.uk	Rupert	Holdsworth	Michael I Holdsworth Limited	The Mill, Manchester Road, Tideswell, Derbyshire, SK17 8LN
future-foundations.co.uk	Jonathan	Harper	Future Foundations Limited	149 Portland Road, London, SE25 4UX, United Kingdom
desertriver.com	Claudia	Werf	Desert River Furniture & Lighting	Warehouse 14, Street 12b, Al Quoz Industrial Area 1, Dubai, United Arab Emirates
sacana.co.uk	Luigi	Koechlin	Sacana Ltd.	Unit A, Logie Court, Stirling University Innovation Park, Stirling, FK9 4NF, Scotland
mertechmarine.co.za	Alwyn	Plessis	Mertech Marine (Pty) Ltd	2 Sturrock Road, Deal Party, Port Elizabeth, 6210, South Africa
23red.com	Jane	Asscher	23red Limited	95 Queen Victoria Street, London, EC4V 4HN, United Kingdom
bsgpropertyservices.co.uk	Andrew	Nunn	BSG Property Services Limited	Lysander Place, Tempsford Airfield, Everton, Sandy, Bedfordshire, SG19 2JW, United Kingdom
lime-retail.co.uk	Dominic	Lennon	Lime Retail	Unit 4, Europark Industrial Estate, Rugby, Warwickshire, CV23 0AL, United Kingdom
iwcf.org	Zdenek	Sehnal	International Well Control Forum	Inchbraoch House, South Quay, Montrose, Angus, DD10 9UA, Scotland
storymuseum.org.uk	Conrad	Bodman	The Story Museum	Rochester House, 42 Pembroke Street, Oxford, OX1 1BP, United Kingdom
adjbusiness.com	Andrew	Josephs	ADJ Business Solutions Ltd	10 Coldbath Square, London, EC1R 5HL, United
jnp.co.uk	Kane	Hennessy	JNP Project Management Ltd	20-22 Wenlock Road, London
curiousuniverse.co.uk	John	Styring	Curious Universe UK Limited	The Ice House, 124-126 Walcot Street, Bath, England, BA1 5BG
infinity-limited.com	Robert	Gunn	Infinity Energy Engineering Limited	Pavilion 2 Kingshill Park, Westhill, Aberdeenshire, Scotland, AB32 6FL
chromalytic.com	Jim	Jeffs	Chromalytic Limited	13 Foxcote Avenue, Peasedown St. John, Bath, England, BA2 8SF
sprezzatura.com		Sprezzatura Ltd	12a Marlborough Place, Brighton, England, BN1 1WN
eastlondonlines.co.uk	Angela	Phillips	Eastlondonlines News Limited	Dept Of Media And Communications, Goldsmiths College, London, England, SE14 6NW
limelightpublicity.co.uk	Garth	Evershed	Limelight Publicity Limited	Regent House, Queens Road, Barnet, Hertfordshire, EN5 4DN
pjinsurancebrokers.co.uk	Peter	Robinson	Eden Insurance Brokers Ltd	Venture House St Leonard's Road, Allington, Maidstone, Kent, ME16 0LS
checkmateservices.com	Vikram	Mahurkar	Checkmate Services Private Limited	GF-6 -9 Amaan Towers, Suvas Colony, Fatehgunj Main Road Baroda, Gujarat 390002, India
dynamicbatteries.co.uk	Glenn	Geldenhuis	Dynamic Battery Services Limited	Unit 1 Gillibrands Road, East Gillibrands, Skelmersdale, Lancashire, WN8 9TA
voluntaryactionangus.org.uk	Hayley	Mearns	Voluntary Action Angus	Third Sector Centre, 5-7 The Cross, Forfar, Angus, DD8 1BX
chrisbartholomew.co.uk	Christopher	Bartholomew	Chris Bartholomew Electrical Contractor Limited	The Barn, 27a South Street, East Hoathly, East Sussex, BN8 6DS
gctpltd.com	Amer	Alghabban	Global Clinical Trial Partners Ltd	272 Bath Street, Glasgow, Scotland, G2 4JR
dennyplastics.co.uk	James	Males	Denny Plastics LLP	Unit 10, Clayfield Mews, Newcomen Road, Tunbridge Wells, Kent, TN4 9PA
grippatank.co.uk	Oliver	Stanton	Grippatank Limited	Units 14–15, Tin Lid Industrial Estate, Brampton Road, Buckden, St Neots, PE19 5YZ
peakindicators.com	Björn	Conway	TPXimpact Data Limited	Hayfield House, Chesterfield, United Kingdom, S41 7ST
andrews-of-tideswell.co.uk	Andrew	Miller	Andrew's of Tideswell Ltd.	Anchor Garage, Tideswell, Buxton, Derbyshire, SK17 8RB
primarycareit.co.uk	Dustyn	Saint	Primary Care IT Ltd	Suite 3a Keswick Hall, Norwich, Norfolk, NR4 6TJ
s-craft.co.uk	Alistair	Simpson	Shuttercraft Ltd (T/A S:CRAFT)	Newdown Farm, Micheldever, Winchester, Hampshire, SO21 3BT
maggsandallen.co.uk	Tim	Maggs	Maggs & Allen	60 Northumbria Drive, Henleaze, Bristol, BS9 4HW
pelhamassociates.com	Sanjeev	Bhamm	Pelham Associates	90 Long Acre, Covent Garden, London, WC2E 9RA
networld.co.uk	Alex	Lovén	Net World Sports Ltd	Bryn Lane, Wrexham Industrial Estate, Wrexham, LL13 9UT
innovatium.co.uk	Simon	Branch	Innovatium Group Limited	9 George Square, Glasgow, G2 1DY
nyt.org.uk	Paul	Roseby	The National Youth Theatre of Great Britain	443-445 Holloway Road, London, N7 6LW
nationalcounsellingsociety.org	Meg	Moss	The National Counselling and Psychotherapy Society Ltd	19 Grafton Road, Worthing, West Sussex, BN11 1QT
shardmediagroup.com	Luke	Broadhurst	Shard Media Group Limited	1-2 Paris Garden, London, SE1 8ND
wannagroup.com	Abba	Abubakar	Wanna Limited	Unit 3, Magna Road, Wigston, Leicestershire, LE18 4ZH
camerakit.ie	Colm	Egan	D+P Multimedia Products Ltd	Unit 1, Terenure Business Park, Beechlawn Way, Terenure Village, Dublin 6W, D6W FY00
groundsmantools.com	Lawrence	Wilson	Groundsman Tools Limited	Prospect House, Unit 4, Old Station Close, Loughborough, Leicestershire, LE12 9NJ
chillipromotions.co.uk	Jody	Fletcher	Chilli Promotional Products Limited	28 High Street, Bidford On Avon, Warwickshire, B50 4AA
1esp.co.uk	Ronan	Lynch	Evesham Specialist Packaging Limited	4th Floor Llanthony Warehouse, The Docks, Gloucester, GL1 2EH
flues.co.uk	Alberto	Pirotta	Canberra Wells Ltd (T/A Flue Stox)	Unit 6, Boston Court, Kansas Avenue, Salford, M50 2GN
sbmonline.co.uk	Melvyn	Brine	SB Online Ltd	123a Allerton Road, Mossley Hill, Liverpool, L18 2DD
craigmyle.org.uk	Siân	Newton	Craigmyle and Company Limited	Wren House, 68 London Road, St Albans, Hertfordshire, AL1 1NG
madeleinelindley.com	Madeleine	Lindley	Madeleine Lindley Limited	Unit 21 & 22, Mandale Park, Greenside Way, Middleton, Manchester, M24 1ZE
sayerssolutions.co.uk	Merewyn	Sayers	Sayers Solutions	16a Chapel Hill, Clayton West, Huddersfield, HD8 9NH
ajenergy.com	John	Simpson	A.J. Energy Consultants Limited	Chalice House, Bromley Road, Elmstead, Colchester, CO7 7BY
mnhscs.com	Matt	Rance	MNH Sustainable Cabin Services Ltd	Rowfant Business Park, Wallage Lane, Rowfant, West Sussex, RH10 4NQ
leonardleese.com	George	Kingham	Leonard Leese Limited	Flat 3, 18 Dane Road, Saint Leonards-on-Sea, TN38 0QN
dsalmoncars.co.uk	Anne	Salmon	D. Salmon Cars Limited	Sheepen Road, Colchester, Essex, CO3 3LE
firstaidscotland.co.uk	Mark	Roberts	First Aid Scotland Limited	272 Bath Street, Glasgow, Scotland, G2 4JR
designamite.co.uk	Thomas	Willcocks	Designamite Ltd	Melrose House, Pynes Hill, Rydon Lane, Exeter, Devon, EX2 5AZ
crescentgarage.co.uk	Semir	Ahmetovic	Crescent Garage Limited	138 Quay Road, Bridlington, YO16 4JB
inspiredknowledge.co.uk	Elizabeth	Birch	Inspired Knowledge Limited	3 Bakers Lane, Shutlanger, Towcester, Northamptonshire, NN12 7RT
desmondeassociates.co.uk	Adam	Desmonde	Desmonde & Associates Ltd	c/o Whyfield Truro Business Park, Threemilestone, Truro, England, TR4 9LF
ebitsllp.com	Richard	Moss	Ebits LLP	Unit 4, Thamesview Industrial Estate, Newtown Road, Henley-On-Thames, RG9 1HG
infodec.co.uk	Keith	Thompson	Infodec Limited	3 Kevan Drive, Send, Woking, Surrey, GU23 7BU
bartonjonespackaging.co.uk	Justin	Burrell	Barton Jones Packaging Limited	Unit 6 Dunhams Court, Dunhams Lane, Letchworth Garden City, Hertfordshire, SG6 1WB
art-press.co.uk	Linzi	Russell-Watson	Artpress Publishing Limited	Adams & Moore House, Instone Road, Dartford, Kent, DA1 2AG
llanelec.co.uk	Spencer	John	Llanelec Precision Engineering Company Limited	Nidum House, Neath Abbey Business Park, Neath Abbey, Neath, SA10 7DR
key-patrol.co.uk	Charles	Lennox	Key Patrol Limited	4th Floor, 28 Kirby Street, London, EC1N 8TE
frankgoulding.co.uk	Aidan	Goulding	Frank Goulding Limited	15 Ludlow Hill Road, West Bridgford, Nottingham, NG2 6HF
serrula-research.com	Humphry	Smith	Serrula Research Limited	Dawes Road Hub, 20 Dawes Road, Fulham, London, SW6 7EN
heritagelincolnshire.org	Tracy	Stringfellow	Heritage Trust of Lincolnshire	The Old School, Cameron Street, Heckington, Sleaford, NG34 9RW
leadingresolutions.com	Pete	Smyth	Leading Resolutions Limited	2 Coped Hall Business Park, Royal Wootton Bassett, Swindon, SN4 8DP
pbdesign.co.uk	Scott	Edsall	PB Design & Developments Ltd	Units 7-10 Hither Green Industrial Estate, Clevedon, BS21 6XT
icon-eng.co.uk	Christopher	Dack	Icon Engineering (Wisbech) Ltd	Europa Way, Wisbech, Cambridgeshire, PE13 2TZ
princethorpe.co.uk	Ed	Hester	The Princethorpe Foundation	Princethorpe College, Princethorpe, Rugby, Warwickshire, CV23 9PX
adkinsresearchgroup.com	Jack	Adkins	Adkins Research Group	7 Trinity Place, Midland Drive, Sutton Coldfield, B72 1TX
glinwellplc.com	Joe	Colletti	Glinwell Public Limited Company	Smallford Nurseries, Hatfield Road, St Albans, Hertfordshire, AL4 0HE
akitasystems.co.uk	Christophe	Boudet	Akita Systems Limited	Unit 15 Nepicar Park, London Road, Wrotham, Kent, TN15 7AF
mesh-energy.com	Doug	Johnson	Mesh Energy Limited	Cambridge House, 8 East Street, Farnham, Surrey, GU9 7RX
innovation1st.com	James	Capel	Innovation 1st Limited	22 Wycombe End, Beaconsfield, Buckinghamshire, HP9 1NB
hi-techproperties.co.uk	David	John	Hi-Tech Property Services Ltd	Unit 16 Davis Way, Fareham, Hampshire, PO14 1JF
plumetyres.co.uk	David	Parker	Plume Tyre Service	343 Stratford Road, Solihull, West Midlands, B90 3BW
sgmlifewords.com	Rob	Taylor	Lifewords (Scripture Gift Mission)	1A The Chandlery, 50 Westminster Bridge Road, London, SE1 7QY
bookmycourse.co.uk	Wayne	Taylor	Book My Course Limited	Citrus Group House, Diamond Way, Nene Park, Irthlingborough, NN9 5QF
originsciences.com	Hugo	Lywood	Origin Sciences Limited	First Floor, 5 Fleet Place, London, EC4M 7RD
womanstrust.org.uk	Yasmin	Rehman	Woman's Trust	West End House, 37 Chapel Street, London, NW1 5DP
west-tpc.co.uk	Gavin	West	West Property Consultants Ltd	216 Banbury Road, Summertown, Oxford, OX2 7BY
calztec.co.uk	James	Haslam	Calztec Ltd	Ws22 Romsley Point, Farley Lane, Romsley, Bromsgrove, England, B62 0LG
plainwords.co.uk	Janet	Basdell	Plain Words Limited	1 Mill Paddock, Abingdon, Oxfordshire, OX14 5EU
be-united.org.uk	Muse	Greenwood	Be United	16 E Cromwell Street, Leith, Edinburgh, EH6 6HD
dzambelis.co.uk	Dimitrios	Zambelis	D Zambelis Ltd	42-44 Cuttlers Road, South Woodham Ferrers, Essex, England, CM3 5XJ
lifeline-fire.co.uk	Jim	Morris	Lifeline Fire and Safety Systems Limited	Falkland Close, Charter Avenue Industrial Estate, Coventry, West Midlands, CV4 8AU
strongrootstraining.com	Jake	Wiid	Strong Roots Training Ltd	Ground Floor, 1-2 Mill Lane, Alton, Hampshire, GU34 2SX
edgeworks.co.uk	Steve	Helsby	The Edge Works Limited	Jactin House, 24 Hood Street, Manchester, England, M4 6WX
pach.co.uk	Christopher	Bennfors	Pach Business Solutions Ltd	8 Market Square, Llandovery, Carmarthenshire, Wales, SA20 0AA
multicad.co.uk	Richard	Huntley	Multicad Solutions Limited	Suite 8 Hawley Manor, Hawley Road, Dartford, Kent, England, DA1 1PX
pharmahygieneproducts.com	Chris	Wilson	Pharma Hygiene Products Limited	Olympus House, Mill Green Road, Haywards Heath, West Sussex, RH16 1XQ
hobbsvalve.com	Alun	Hobbs	Hobbs Valve Limited	Unit 16 Baglan Way, Baglan Industrial Park, Port Talbot, Wales, SA12 7BY
mmpaccountants.co.uk	Andrew	Gaete	MMP Limited (T/A Michael Martin Partnership)	18/20 Canterbury Road, Whitstable, Kent, CT5 4EY
michaelparkes.co.uk	Denise	Ford	Michael Parkes Surveyors Limited	C6 Laser Quay, Culpeper Close, Medway City Estate, Rochester, Kent, ME2 4HU
enjoycarhire.com	Martin	Mansell	Enjoy Travel Technology Limited	Unit 7 Borers Yard, Borers Arms Road, Copthorne, Crawley, West Sussex, RH10 3LH
arionltd.co.uk	Russ	Pryor	Arion Training & Development Ltd	Salus House, Valley Gate, Sleaford, Lincolnshire, NG34 8YY
leeandlindars.com		Lee & Lindars (Oxford) Limited	94 High Street, Thame, Oxfordshire, OX9 3EH
excess-energy.co.uk	Fraser	Gardiner	Excess Energy Communications Limited	Handeeps Tregonhawke, Whitsand Bay, Millbrook, Torpoint, Cornwall, PL10 1JX
hillmount.co.uk	Robin	Mercer	Hillmount Ltd (T/A Hillmount Garden Centre)	56-58 Upper Braniel Road, Gilnahirk, Belfast, BT5 7TX
shiresresidential.com	Robert	Love	Shires Residential	4 New Street, Mildenhall, Suffolk, IP28 7EN
titansurveys.com	Malcolm	Houston	Titan Environmental Surveys Limited	Endeavour House, Admiralty Road, Great Yarmouth, Norfolk, NR30 3NG
wmtmarine.com	John	Kenny	WMT Marine Ltd	Dee House, Parkway, Zone 2, Deeside Industrial Park, Flintshire, CH5 2NS
davrosteel.co.uk	Richard	Evans	Davro Steel Limited	Unit 9, Hayes Trading Estate, Hingley Road, Halesowen, West Midlands, B63 2RR
ctp.ae	Sanjay	Shah	City Travel Point LLC	Shop #245, Al Dhiyafa Rd, Satwa (Near Satwa Roundabout), Dubai, United Arab Emirates
1stdirectpools.com	Francesca	Bailey-Wheeler	1st Direct Pools	Ambassador Business Park, West Stour, Gillingham, Dorset, SP8 5SE
reheat.uk.com	Ben	Tansey	Reheat (Renewable Technologies) Limited	First Floor, Lion House, Willowburn Trading Estate, Alnwick, Northumberland, NE66 2PF
brocktaylor.co.uk	Peter	Maskell	Brock Taylor Limited	2-4 East Street, Horsham, West Sussex, RH12 1HL
bibliothequedesign.com	Timothy	Beard	Bibliothèque Design Limited	1–5 Clerkenwell Road, London, EC1M 5PA
plasmotec.co.uk	James	Rankin	Plasmotec Limited	G2-G4 Lincoln Park, Ward Road, Buckingham Road Industrial Estate, Brackley, Northamptonshire, NN13 7LE
transpakship.co.uk	Stephen	Oldershaw	Transpakship International Limited	Export Drive, Fulwood Industrial Estate, Sutton-in-Ashfield, Nottinghamshire, NG17 6AF
tatra.co.uk	Paul	Freud	Tatra Rotalac Limited	Southmoor Road, Wythenshawe, Manchester, M23 9DS
walkerhumphreyltd.co.uk	Martin	Humphrey	Walker Humphrey Limited	Unit 15 Seafox Court, Sherburn In Elmet, Leeds, LS25 6PL
squarebook.co.uk	Joseph	Sluys	Square Book Limited	25a Thistle Street South West Lane, Edinburgh, EH2 1EW
croftarchitecture.com	Carl	Croft	Croft Architecture Limited	6/7 Pearl House, Anson Court, Beaconside, Stafford, ST18 0GB
prospectresourcing.com	Colette	Brown	Prospect Resourcing Limited	8 The Sycamores, Bishop's Stortford, Hertfordshire, CM23 5JR
totalperformancedata.com	Will	Gordon	Total Performance Data Limited	6 Derby Street, London, W1J 7AD
groupmedianet.com	Gideon	Clifton	Medianet Ltd	4 Nottingham Street, London, W1U 5EQ
printdatasolutions.co.uk	Nicholas	Shelton	Print Data Solutions Limited	12 Regent Park, Booth Drive, Park Farm Industrial Estate, Wellingborough, NN8 6GR
woollardandhenry.com	Bruce	Gill	Woollard & Henry Limited	Stoneywood Park, Dyce, Aberdeen, AB21 7DZ
jempsons.com	Stephen	Jempson	Jempsons Limited	Main Street, Peasmarsh, Nr Rye, East Sussex, TN31 6YD
ontech.co.uk	Oliver	Gee	Ontech Solutions Ltd	The Quadrant, Primrose Hill, Doddington, March, Cambridgeshire, PE15 0SU
westaflex.com.au	Elizabeth	Sterling	Westaflex (Aust) Pty Ltd	140-150 National Boulevard, Campbellfield, VIC 3061, Australia
pantheonpropertyservices.co.uk	Ryan	O'Connor	Pantheon Property Services Limited	18-20 Hill Street, Liverpool, L8 5SG
simply-sustainable.co.uk	Alastair	MacGregor	Simply Sustainable Limited	Unit 1, The Old Dairy, Home Farm, Ardington, Wantage, OX12 8PD
thisisrms.co.uk	Ruth	Shearn	Retail Merchandising Services Limited	Unit 1, Cleppa Park, Newport, NP10 8BA
jbcoachworks.co.uk	James	Biggam	J B Coachworks Limited	Unit 1, Mill Hall Business Estate, Aylesford, Kent, ME20 7JZ
bbbind.com	Duncan	Gillis	BBB Industries, LLC	2400 20th Avenue SE, Daphne, AL 36526, USA
deepcove.eu	Roland	Allen	DeepCove Limited	35 Ballards Lane, London, N3 1XW
eurovalve.co.uk	Nicolas	Pond	Eurovalve UK Limited	Unit 1, Riverside Court, Don Road, Sheffield, S9 2TJ
testvalleypkg.co.uk	Jerry	Steedman	Test Valley Limited	26-27 Walworth Road, Walworth Business Park, Andover, Hampshire, SP10 5LH
office.bm	B.	Dickinson	AF Smith	7 Tumkins Lane, Hamilton, HM 19, Bermuda
bonaccordengineering.com	Jill	Leiper	Bon Accord Engineering Ltd	20-22 Wenlock Road, London, England, N1 7GU
ctech-europe.com	Daniel	Davies	CTech Europe Ltd	Unit 2 Rovert House, Water Tower Road, Clayhill Industrial Estate, Neston, South Wirral, CH64 3US
westendgarage.net	Brendan	Dunne	West End Garage (2024) Limited	28 Queen Street, Broughty Ferry, Dundee, DD5 1AN
ameriscot.co.uk	Robert	Kay	Ameriscot Commercial Limited	Unit 1 Bournemouth House, 19 Christchurch Road, Bournemouth, Dorset, BH1 3LJ
servicepower.ltd.uk	Frank	Gelbart	Servicepower Limited	Rosse Works, Moorhead Lane, Shipley, West Yorkshire, BD18 4JH
twinklesnurseries.com	Jill	Johnson	Twinkles Nurseries Limited	231 Higher Lane, Lymm, Cheshire, England, WA13 0RZ
icsmcredit.com	Ian	Carrotte	ICSM Credit Ltd	The Exchange, Express Park, Bristol Road, Bridgwater, Somerset, TA6 4RR
ipsltd.biz	Jim	Stephanou	IPS Product Supplies Limited	Summit House, 4-5 Mitchell Street, Leith, Edinburgh, Scotland, EH6 7BD
premiervend.co.uk	Darren	Herbert	Premier Vending Services Ltd	Unit 15 Evans Business Centre, Minerva Avenue, Chester West Employment Park, Chester, CH1 4QL
eazychem.co.uk	Marc	Sfakianakis	Eazychem Limited	Unit 10, Whittle Road, Ferndown Industrial Estate, Wimborne, Dorset, BH21 7RU
rowleys.biz	Copson	Tom	The Rowleys Partnership Ltd	Charnwood House, Harcourt Way, Meridian Business Park, Leicester, LE19 1WP
envirowales.co.uk	Paul	Walters	Envirowales Limited	Faulkner House, Victoria Street, St Albans, Hertfordshire, AL1 3SE
eastlinklanker.com	Zeljko	Popovic	Eastlink Lanker PLC	10 Manchester Square, London, W1U 3NL
marketingmeans.co.uk	Christopher	Bowden	Marketing Means (UK) Limited	Suite 3 Second Floor, Higher Mill, Higher Mill Lane, Buckfastleigh, Devon, TQ11 0EN
the-method.com	Mark	Smith	Method (UK) Limited	The Dairy, Manor Courtyard, Aston Sandford, Buckinghamshire, HP17 8JB
salestransformation.co.uk	Simon	Breese	Sales Transformation Limited	Wymund House, 46b Brook Street, Wymeswold, Loughborough, LE12 6TU
fluidearthsystems.com	Martin	Davis	Fluid Earth Systems Limited	c/o Francis Clark LLP, Unit 18, 23 Royal William Yard, Plymouth, Devon, PL1 3GW
vtech.me.uk	Viresh	Chandarana	VTech Electronics Europe PLC	Napier Court, Abingdon Science Park, Abingdon, Oxfordshire, OX14 3YT
abtengineering.com	Paul	Ross	ABT Engineering Limited	7 Colquhoun Avenue, Hillington, Glasgow, G52 4BN
windsorleadership.org.uk	Jo	Youle	The Windsor Leadership Trust	120-125 Peascod Street, Windsor, Berkshire, SL4 1DP
priorsfieldschool.com	Julia	Huxley	Prior's Field School Trust Limited	Priorsfield Road, Godalming, Surrey, GU7 2RH
hoshizaki.co.uk	Simon	Frost	Hoshizaki Europe Limited	Telford 70 Stafford Park 7, Telford, Shropshire, TF3 3BQ
keyyachting.com	Bill	Stringer	Key Yachting Ltd	Ground Floor Office Firefly House, Firefly Road, Hamble Point Marina, Hamble, Southampton, SO31 4NB
sofasofa.co.uk	Lloyd	Ridgwell	Sofa Sofa Limited	Viaduct Works, Crumlin Road, Crumlin, Newport, Gwent, NP11 3PL
ga-security.co.uk	Jay	Graham	G and A Security NE Ltd	Suite 2.05 Swans Centre For Innovation, Station Road, Wallsend, NE28 6EQ
retailgazette.co.uk	Sean	Brierley	Retail Gazette Limited	7 Alrewic Gardens, Aldridge, Walsall, WS9 8NT
celestialwindows.co.uk	Alan	Sewell	Celestial Windows and Conservatories Limited	Unit 1 Simcox Court, Riverside Industrial Estate, Middlesbrough, Cleveland, TS2 1UX
gmecsolutions.com	Gavin	Tuck	GMEC Solutions Limited	Apollo Business Village, Heol Persondy, Aberkenfig, Bridgend, CF32 9TF
trh.co.uk	Danny	Cohen	Theatre Royal Haymarket	Haymarket, London. SW1Y 4HT
lenochengineering.com	John	Rushbrooke	Lenoch Engineering Limited	56 Somers Road, Somers Road Industrial Estate, Rugby, Warwickshire, CV22 7DH
dupremarine.co.uk	Tobias	du-Pre	du Pré Marine Ltd	Unit 2, The Old Dairy, Standen Manor, Hungerford, Berkshire, RG17 0RB
gas4air.co.uk	Kieron	Griffin	Griffin Air Systems Ltd	12 North Avenue, Clydebank Business Park, Clydebank, G81 2QP
betterequipped.co.uk	Helen	Mackenzie	Better Equipped Educational Supplies Ltd	18-20 Moorland Road, Burslem, Stoke-on-Trent, Staffordshire, ST6 1DW
central-hygiene.co.uk	Richard	Jones	Central Hygiene Limited	Westminster House, 10 Westminster Road, Macclesfield, Cheshire, SK10 1BX
safeland.co.uk	Larry	Lipman	Safeland Limited	1a Kingsley Way, London, N2 0FW
omcmotorgroup.co.uk	Jonathan	Eglin	O.M.C. Motor Group Limited	1 Manchester Road, Oldham, Lancs, OL8 4AU
dinstock.com	Steven	Paskin	Dinstock Limited	Unit C3, Hortonwood 10, Telford, Shropshire, TF1 7ES
kularfashion.com	Sukhpal	Singh	Kular Fashion Limited	17-21 Ferryquay Street, Derry, BT48 6JB
operanorth.co.uk	Laura	Canning	Opera North Limited	Grand Theatre, 46 New Briggate, Leeds, West Yorkshire, LS1 6NU
ecommquest.com	Chris	Walsh	Ecommquest Limited	1st Floor, Sackville House, 143-149 Fenchurch Street, London, EC3M 6BL
hbtc.co.uk	Johanna	Rudd	Hull Business Training Centre Limited	2 Charlotte Street Mews, Hull, HU1 3BP
yomdel.com	Andy	Soloman	Yomdel Limited	Brindley House Outrams Wharf, Little Eaton, Derby, DE21 5EL
c-21.co.uk	Christina	Clarke	C21 Creative Communications Ltd	The Court House, 9 Grafton Street, Altrincham, Cheshire, WA14 1DU
rhadvertising.co.uk	Paul	Ridgers	RH Advertising Limited	Richmond Court, Emperor Way, Exeter, Devon, EX1 3QS
goddardspies.com	Jeff	Goddard	Goddards (Wrights Pies)	3 High Street, Wellington, Somerset, TA21 8QT
stopgap.co.uk	Claire	Owen	Stopgap Limited	Goodwin House, 5 Union Court, Richmond, London, TW9 1AA
hflettings.co.uk	Laura	Larkin	H F Lettings Ltd	16 High Street, Corsham, SN13 0HB
rnltd.co.uk	Peter	Robinson	RN (Recruitment Network) Ltd	Suite 101, 1-2 Paris Garden, London, SE1 8ND
sew-fine.co.uk	Guy	Powis	Sew-Fine Ltd	160 Watford Road, Croxley Green, Rickmansworth, Hertfordshire, WD3 3BZ
bluewren.co.uk	Michael	Lough	Blue Wren Limited	Unit 16, Eastway Business Village, Olivers Place, Fulwood, Preston, PR2 9WT
voycepullin.co.uk	Chris	Voyce	Voyce Pullin Limited	Cornerstone House, Midland Way, Thornbury, Bristol, BS35 2BS
millfieldautoparts.co.uk	Abbas	Damani	Millfield Autoparts Limited	Unit 5 Bourges View Park, Maskew Avenue, Peterborough, PE1 2FG
goldingaudio.co.uk	Joseph	Patrick	Golding Audio Limited	Suite E2, 2nd Floor, The Octagon, Middleborough, Colchester, Essex, CO1 1TG
sitwellinvestments.com	Noel	Spiteri	Sitwell Investments Limited	Heage Road Industrial Estate, Heage Road, Ripley, Derbyshire, DE5 3GH
pioneerclub.co.uk	Danny	Clare	Pioneer Club St. Albans CIC	Pioneer Club, Heathlands Drive, St Albans, Hertfordshire, AL3 5AY
anybook.biz	Eliran	Navon	Anybook Limited	28 West End, Burgh Le Marsh, Skegness, Lincolnshire, PE24 5EY
printsolutions.co.uk	Christopher	Slocock	Print Solutions (.co.uk) Limited	The Old Brewery, 14-15 Mill Lane, Wimborne, Dorset, BH21 1LN
davidsmithcontractors.com	David	Smith	David Smith Contractors Ltd	Cairnmuir, Memsie, Fraserburgh, Aberdeenshire, AB43 7AR
vr-tek.co.uk	Dave	Pearce	VR-Tek Ltd	5 Colts Croft, Great Chishill, Royston, Hertfordshire, SG8 8SF
rowhamsteel.co.uk	Trevor	Mizon	Rowham Steel Products Limited	Lyons Road, Trafford Park, Manchester, M17 1RN
apexwiringsolutions.co.uk	Dave	Lewis	Apex Wiring Solutions Ltd	St. Johns Road, Meadowfield Industrial Estate, Durham, DH7 8RJ
yc.uk.com	Paul	Alsop	YC Tech Limited	Office 1, The Store Room, 671 Eccles New Road, Salford, M50 1AY
orchardinteriors.co.uk	Rebecca	Griffiths	Orchard Interiors Limited	1 Redmine Close, Brymbo Road Industrial Estate, Newcastle-under-Lyme, Staffordshire, ST5 9HZ
bathpropertymaintenance.co.uk	Philip	Adams	Bath Property Maintenance Ltd	3 Bramhall Place, Storeys Bar Road, Peterborough, Cambridgeshire, PE1 5YS
cliftonrubber.co.uk	Brian	Burton	Clifton Rubber Company Limited	8 Edison Road, St. Ives, Cambridgeshire, PE27 3FF
cardandpaymentsawards.com	Michael	Harty	The Card and Payments Awards Ltd	2-4 Petworth Road, Haslemere, Surrey, GU27 2HR
sppropertygroup.com	Jo	Eccles	Select Property Group Limited	Horsley House, Regent Terrace, Alderley Edge, Cheshire, SK9 7JZ
midtherm.co.uk	Paul	Ferris	Midtherm Flue Systems Limited	Midtherm House, Midtherm Business Park, New Road, Netherton, Dudley, DY2 8SY
printer-graphics.com	Natasha	Parlett	Printer Graphics Ltd	Unit 7, Larchwood Avenue, Havant, Hampshire, PO9 3BE
heraldchase.com	Nigel	Elkes	Herald Chase Marketing Limited	4b Paddock Road, Caversham, Reading, RG4 5BY
quadrantresourcing.com	Benjamin	Taylor	Quadrant Resourcing Ltd	7 Bell Yard, London, United Kingdom, WC2A 2JR
triad.uk.com	David	Hummel-Newell	Triad UK Limited	Triad House, Mountbatten Court, Worrall Street, Congleton, CW12 1DT
clement-clarke.com	Marc	Davies	Clement Clarke International Ltd	Cwm Cynon Business Park, Mountain Ash, Rhondda Cynon Taf, CF45 4ER
architen.com	Christopher	Rowell	Architen Limited	Station Yard Industrial Estate, Station Road, Chepstow, NP16 5PF
positiveimagesuk.com	Danny	Sullivan	Positive Images Design & Exhibitions Ltd	6th Floor Linen Hall, 162-168 Regent Street, London, W1B 5TG
stylecafe.co.uk	Roger	Heap	Style Cafe Limited	Vivary Mill, Vivary Way, Colne, Lancashire, BB8 9NW
ohmenergy.co.uk	Jason	Lindfield	Ohm Energy Limited	A2 Ropemaker Park, Diplocks Way, Hailsham, East Sussex, BN27 3GU
deckpro.uk.com	Michael	Marks	Deckpro Ltd	Unit A3 Lion Business Park, Dering Way, Gravesend, DA12 2DN
mccolgans.ie	William	McColgan	McColgan's Quality Foods Ltd	Dublin Road Industrial Estate, Strabane, Co. Tyrone, BT82 9EA
crushers4sale.com	Paul	McGoldrick	Crushers 4 Sale Ltd	The Croft, Fore Street, Weston, Honiton, Devon, EX14 3PF
laurentgiles.co.uk	David	Lewis	Laurent Giles Naval Architects Limited	Units 110-112 Brockenhurst Business Centre, Grigg Lane, Brockenhurst, SO42 7RE
cobaltpropertypartners.com	Edward	Mitchell	Cobalt Property Partners Limited	Fifth Floor The Lantern, 75 Hampstead Road, London, NW1 2PL
hyquip.co.uk	Paul	Taylor	Hyquip Limited	New Brunswick Street, Horwich, Bolton, Lancashire, BL6 7JB
elimhq.net	Mark	Pugh	Elim Foursquare Gospel Alliance	Elim International Centre, De Walden Road, West Malvern, WR14 4DF
definitionagency.com	Louise	Vaughan	Definition Agency Limited	One Park Row, Leeds, LS1 5HN
craigheadcountrynursery.co.uk	Elspeth	Goldie	Craighead Country Nursery School	Craighead Country Nursery School, Mauchline, Ayrshire. KA5 6EX
ascendantaccess.com	Steve	Dean	Sunlift Ltd (T/A Ascendant Access)	Unit 1 Tilley Road, Crowther Industrial Estate, Washington, NE38 0AE
chemquest.co.uk	Yvonne	Hayes	ChemQuest Limited	97 Alderley Road, Wilmslow, SK9 1PT
parkeray.co.uk	Phil	Pearce	Parkeray Limited	2nd Floor, 24 King William Street, London, EC4R 9AT
sinclairhammelton.co.uk	Russell	Sinclair	Sinclair Hammelton Limited	Ground Floor, 1-7 Station Road, Crawley, West Sussex, RH10 1HT
bekstone.co.uk	Ankur	Gupta	Bekstone UK Limited	Burford Quarry, Burford Road, Brize Norton, Oxfordshire, OX18 3WN
bvgassociates.com	Bruce	Valpy	BVG Associates Limited	Hermes House, Fire Fly Avenue, Swindon, Wiltshire, SN2 2GA
hotelrez.net	Mark	Lewis	HotelREZ Limited	Office 5 Newark Beacon, Beacon Hill Office Park, Cafferata Way, Newark, Nottinghamshire, NG24 2TN
talkingfinances.co.uk	Chris	Masters	Talking Finances Ltd.	Solo House, The Courtyard, London Road, Horsham, West Sussex, RH12 1AT
spck.org.uk	Sam	Richardson	The Society for Promoting Christian Knowledge	Studio 101, The Record Hall, 16-16A Baldwins Gardens, London, EC1N 7RJ
jsacs.com	John	Sacks	JSA Consultancy Services	4th Floor, Gray's Inn Chambers, Gray's Inn, London, WC1R 5JA
wimpy.uk.com	Chris	Woolfenden	Wimpy Restaurants Group Limited	2 The Listons, Liston Road, Marlow, Buckinghamshire, SL7 1FD
glass-design.net	Vince	McDonnell	Glass Designs Limited	Units 3 & 4, City Cross Business Park, Salutation Road, London, SE10 0AT
airconditioningcentre.com	Julian	Martin	Air Conditioning Centre	Unit 8, Milton Business Centre, Wick Drive, New Milton, Hampshire, BH25 6RH
edenfyfe.com	Lisa	Bray	Eden Fyfe Accounts Limited	Unit 5, New Grange Business Village, Pittenweem Road, Anstruther, Fife, KY10 3QS
medialicensingco.com	Richard	Coury	Media Licensing Co.	38 Craven Street, London, WC2N 5NG
highlanderinternational.co.uk	Brian	Bingham	Highlander International Recycling Limited	7-10 Linwood Avenue, East Kilbride, Glasgow, G74 5NE
chooseleads.co.uk	Jade	Bustorff-Silva	Choose Leads Limited	7 Bell Yard, London, WC2A 2JR
itspr.co.uk	Waj	Hussain	ITS PR Limited	6 Mandeville Place, London, W1U 2BQ
kendonflexocare.co.uk	Alistair	Kendon	Kendon Flexocare Limited	37 Wigman Road, Bilborough, Nottingham, NG8 4PA
thebmgc.com		The Blue Moose Graphic Company Limited	The Homestead, Park Lane, Charvil, Berkshire, RG10 9TR
fletchereuropean.co.uk	Colin	Fletcher	Fletcher European Containers Limited	49-51 Sanders Road, Finedon Road Industrial Estate, Wellingborough, NN8 4NL
fleetsource.co.uk	Nick	Caesari	Fleet Source Limited	Unit A2 Devonshire Business Centre, Works Road, Letchworth Garden City, SG6 1GJ
corecreative.co.uk	Matthew	Hellier	Core Creative Ltd	C/O Maltravers House, Petters Way, Yeovil, Somerset, BA20 1SH
bjcs.co.uk	Matthew	Bradley	Bradley & Jefferies Solicitors Limited	3 College Place, Derby, DE1 3DY
henleyinvestments.com	Ian	Rickwood	Henley Investment Management Ltd	50 Grosvenor Hill, London, W1K 3QT
stcongar.com	Miff	Chichester	St. Congar Properties Limited	Lower Hayne Farm, Marsh Road, Shabbington, Buckinghamshire, HP18 9HF
star-international.co.uk	Jeff	Antley	Star International Limited	Star House, Turbine Road, Birkenhead, Merseyside, CH41 9BA
ibms.org	David	Wells	Institute of Biomedical Science	12 Coldbath Square, London, EC1R 5HL
ccrbuilding.net	Arne	Madsen	C.C.R. Building Services Limited	Suite K, Priest House, 1624 High Street, Knowle, Solihull, B93 0JU
onestoppropertysolutions.com		Shrigley Rose & Co	Shrigley Rose & Co, 4 Ravenoak Road, Cheadle Hulme, Greater Manchester, SK8 7DL
developandpromote.co.uk	Darren	Hickie	Develop and Promote Ltd	463-465 High Street, Lincoln, LN5 8JB
cosway.co.uk	Ory	Halperin	Cosway Estates	135/137 The Broadway, Mill Hill Circus, London, NW7 4TD
firstsubsea.com	Jonathan	Barnett	First Subsea Limited	Unit 432, Walton Summit Centre, Bamber Bridge, Preston, Lancashire, PR5 8AU
bplmarketing.com	Chris	Dry	BPL – The Business Partnership Limited	95 Southwark Street, London, SE1 0HX
fouldslifts.co.uk	Catherine	Ogden	E.A. Foulds Limited	Suites 1-4 Holker Business Centre, Burnley Road, Colne, Lancashire, BB8 8EG
unitedcorporation.co.uk	Karim	Fatehi	United Corporation Ltd.	30 Stafford Road, Wallington, Surrey, SM6 9AA
vector7.co.uk	John	Vincent	Vector 7 Ltd	107 High Street, Honiton, Devon, EX14 1PE
tmgtraining.co.uk	Keith	Daniell	TMG Holdings and Training Ltd.	The Tithe Barn, 5 College Street, East Bridging, Nottingham, NG13 8LE
gkstrategy.com	Louise	Allen	GK Strategy Limited	Frameworks, 52 Horseferry Road, Westminster, London, SW1P 2AF
techinspections.co.uk	Dominic	Moran	Tech Inspections Ltd	Unit 11, 1-2 North End, Swineshead, Boston, Lincolnshire, PE20 3LR
validpath.co.uk	Angus	MacNee	ValidPath Limited	The Maltings, East Tyndall Street, Cardiff, CF24 5EA
targetgroup.co.uk	Peter	O'Connor	Target Group Limited	Imperial Way, Coedkernew, Newport, NP10 8UH
kinshipcreative.uk	Nick	Tobias	Kinship Creative Ltd	209 Foundry, 4 New Acres Lane, London, SW18 1HT
bowlandtreeconsultancy.co.uk	Phillip	Harris	Bowland Tree Consultancy Ltd	6 Cross Street, Preston, Lancashire, PR1 3LT
workman.co.uk	Matthew	Pateman	Workman LLP	80 Cheapside, London, EC2V 6EE
mac-solutions.co.uk	Ian	Bailey	M.A.C. Solutions (UK) Limited	Unit 1 Oakfield Road, Cheadle Royal Business Park, Cheadle, Cheshire, SK8 3GX
medfor.co.uk	Robert	Fisher	Medfor Products Limited	Sherwood House, 41 Queens Road, Farnborough, Hampshire, GU14 6JP
hopsls.com	Jimmy	Davies	HOPS Labour Solutions Limited	Overross House, Ross Park, Ross-On-Wye, HR9 7US
racinguk.com	Nick	Mills	Racecourse Media Group Limited	10th Floor, The Met Building, 22 Percy Street, London, W1T 2BU
cetus-solutions.com	Jacob	Kronborg	Proact Deutschland GmbH	Südwestpark 43, 90449 Nuremberg,
hafrenfasteners.com	Matthew	Lynes	Hafren Fasteners Limited	Unit 23, Mochdre Industrial Estate, Mochdre, Newtown, Powys, SY16 4LE
gmpcom.com	Giby	George	GMP Healthcare Ltd	Park Royal House, Valletta Street, Hull, HU9 5NP
ryejazz.com	Ian	Bowden	Rye International Jazz Festival Limited	Bewl Bridge Farmhouse, Hastings Road, Lamberhurst, Kent, TN3 8JJ
grantbarnett.com	Paul	Thomas	Grant, Barnett & Company, Limited	Waterfront House, 55-61 South Street, Bishop's Stortford, Hertfordshire, CM23 3AL
stainlesssteelservices.co.uk	Darren	Moult	Stainless Steel Services Limited	Unit 16, Junction 6 Industrial Estate, Electric Avenue, Birmingham, B6 7JJ
dsgroup.uk.com	Kevin	Auchoybur	The DS Group (Direct Solutions Limited)	Unit 1, Horizon Point, Spilsby Road, Harold Hill, Romford, RM3 8SB
smia.org.uk	Robert	Kilpatrick	Scottish Music Industry Association Limited	35 Ballards Lane, London, N3 1XW
wymbsengineering.com	Brendan	Wymbs	Wymbs Engineering Limited	Unit 7, Silk Way, Macclesfield, SK10 2BB
sunflowermusic.co.uk	Paul	Dimmock	Sunflower Music Limited	59-60 Russell Square, London, WC1B 4HP
systempak.net	Edward	Morgan	Systempak Limited	Unit 4, Mead Park, River Mead, Harlow, Essex, CM20 2SE
jlssolicitors.co.uk	Justine	Soper	JLS Solicitors Limited	High Point, Church Street, Send, Woking, Surrey, GU23 7JR
psicon.co.uk	Daniel	Simmonds	Psicon Limited	15 New Dover Road, Canterbury, Kent, CT1 3AS
safests.com	Yvonne	Mason	SafeSTS Limited	Unit 18, Diss Business Centre, Dark Lane, Scole, Diss, IP21 4HD
lovekates.co.uk	Kate	Malt	Love Kate's (Kates (UK) Limited)	Unit 1, Boundway Business Park, Sway, Lymington, Hampshire, SO41 6EN
acgoldelectrical.co.uk	Alasdair	Campbell	AC Gold Electrical Services Ltd	18-20 Stirling Road, Airdrie, North Lanarkshire, ML6 7JA
sugarmarketing.co.uk	Martin	Long	Sugar Marketing Limited	179-181 High Street, West Wickham, Kent, BR4 0LP
contisgroup.com	Peter	Cox	Contis Group Limited	Navigation House, Belmont Wharf, Skipton, North Yorkshire, BD23 1RL
adproducts.com	Steven	Elliott	Product Source Group Limited	Unit 6 Rhodes Business Park, Silburn Way, Middleton, Manchester, M24 4NE, UK
sbc-training.co.uk	Colin	Thaw	SBC Training Limited	2-4 Roushill, Shrewsbury, Shropshire, SY1 1PN
just-desserts.co.uk	Younis	Chaudhry	Just Desserts (Yorkshire) Ltd	Unit 46, Station Road, Shipley, West Yorkshire, BD18 2JL
mkwcreative.com	Michelle	Wintersteen	McKay Williamson.	The Old War Office, Res 2.11, Delivery Bay, Whitehall Place, London SW1A 2EU
ease.ltd.uk	Lin	Dai	Ease Industries & Investments Co., Ltd	Unit 5, Staples Business Park, 1000 North Circular Rd., NW2 7JP London, United Kingdom
clipperukltd.co.uk	Lina	Hu	Clipper UK Ltd	Unit 5, The Ermine Centre, Hurricane Close, Huntingdon, PE29 6XX
acservicessouthern.co.uk	Hellen	Hagger	AC Services (Southern) Ltd	Unit 15, Windrush Business Park, Witney, OX29 7EU
snatchpac.co.uk	David	Ashburn	Snatchpac Limited	Unit 5, Newporte Business Park, Bishops Road, Lincoln, LN2 4SY
mercoservices.com	Neil	Fagleman	Merco Services Limited	Beech Court, M60 Office Park, Wynne Avenue, Swinton, Manchester, M27 8FF
sim.co.uk	Hassan	Taher	SIM International (UK)	6 Trust Court, Histon, Cambridge, England, CB24 9PW
bmvcaravans.co.uk	Jeff	Wentworth	Blackmore Vale Leisure Ltd	Sherborne Causeway, Shaftesbury, Dorset, SP7 9PX
cjpropertymarketing.com	Carl	Jones	CJ Property Marketing Limited	First Floor Flint House, Flint Barn Court, Church Street, Old Amersham, Buckinghamshire, HP7 0DB
scullyuk.com	Eric	Kirleis	Scully U.K. Limited	Meridian House, Unit 33, 37 Road One, Winsford Industrial Estate, Winsford, Cheshire, CW7 3QG
chaseandcoadvertising.co.uk	James	Partridge	Chase & Co Advertising Ltd	Lakeview House, 4 Woodbrook Crescent, Billericay, Essex, CM12 0EQ
scgsupplies.co.uk	Stephen	Grieve	SCG Supplies Limited	64b Rochsolloch Road, Airdrie, North Lanarkshire, Scotland, ML6 9BG
jpsuppliesltd.co.uk	Paul	Bubb	J P Supplies (Crawley) Limited	Unit 2 Spindle Way, Crawley, West Sussex, RH10 1TG
holmesteel.co.uk	Samantha	Chapman-Wicks	Holme Steel Fabricators Ltd.	2 Bessemer Way, Sawcliffe Industrial Park, Scunthorpe, DN15 8XE
estatsolutions.co.uk	Jeremy	Ellis	eStat Solutions Ltd	Unit 20, Horton Court, Hortonwood 50, Telford, Shropshire, TF1 7GY
jutebag.co.uk	Rakesh	Goel	Jute Trading Ltd	Jute Trading Ltd, Unit 370, Centennial Park, Centennial Avenue, Elstree, Borehamwood, WD6 3TJ, UK
radprint.com	Barry	Miller	RAD Printing	Unit 16, Northfleet Industrial Estate, Lower Road, Northfleet, Kent, DA11 9SW
archeslightingcentre.co.uk	Christopher	Thompson	Arches Lighting Centre	16-22 Upper Newtownards Road, Belfast, BT4 3EL
ullesthorpecourt.co.uk	David	Thomas	Ullesthorpe Court Hotel & Golf Club	Frolesworth Road, Lutterworth, Leicestershire, LE17 5BZ
mackinnonandsaunders.com	Ian	Mackinnon	Mackinnon & Saunders Limited	1-2 Block D, Altrincham Business Park, Stuart Road, Altrincham, WA14 5GJ
uni-play.co.uk	Victoria	Smith	UniPlay It's Educational Ltd.	3-5 Centurion Court, Leyland, Lancashire, PR25 3UQ
leylandsdm.co.uk	Jonathan	Jennings	Leyland SDM Limited	Unit 24, Fourth Way, Wembley, HA9 0LH
f1manufacturing.com	Paul	Attridge	F1 Manufacturing Limited	350 Melton Road, Leicester, LE4 7SL
thirdlifecare.co.uk	Duncan	Beaton	Third Life Care Limited	39 High Street, Battle, East Sussex, TN33 0EE
halle.co.uk	David	Butcher	The Hallé Concerts Society	Hallé St Peter's, 40 Blossom Street, Ancoats, Manchester, M4 6BF
cep.org.uk	Tim	Jones	Community Energy Plus	Suite C, Milestone House, Glenthorne Court, Threemilestone, Truro, Cornwall TR4 9NY
britanniaits.com	Amanda	Hutton	Britannia Safety and Training	Britannia Safety and Training, Unit 18, Britannia House, Wymondham, Norfolk, NR18 9SB, United Kingdom
aviateq.com	Lynette	Reynolds	Aviateq Limited	Unit 1, Oakfield Road, Cheadle Royal Business Park, Cheadle, SK8 3GX
falanx.com	Bill	Dawson	Wavenet Limited	Wavenet HQ, One Central Boulevard, Blythe Valley Park, Solihull, West Midlands, B90 8BG
tms-ltd.net	Paul	Beckett	Total Machining Solutions	Unit 14, Lordswood Industrial Estate, Revenge Road, Lordswood, Kent, ME5 8UD
pipeline-products.co.uk	Matthew	Jones	Pipeline Products Limited	Unit 1, Westpoint Trading Estate, Westpoint Road, Bristol, BS3 2JZ
rhino-exteriors.co.uk	Dan	Finch	Rhino Exteriors Limited	Unit 7, The IO Centre, Fiddlebridge Lane, Hatfield, AL10 9EB
aai-intl.co.uk	Lalita	Kanetkar	A.A.I. (International) Limited	10 Bridge Street, Christchurch, Dorset, BH23 1EF
thepackagingsite.co.uk	James	Hilson	The Packaging Site	Unit 28, Bizspace, Courtwick Lane, Littlehampton, West Sussex, BN17 7TL
academyclass.com	Mark	Young	Academy Class Limited	609 Linen Hall, 162-168 Regent Street, London, W1B 5TG
twg-systems.co.uk	Andrew	Twigg	TWG Systems Limited	Beacon House, Stokenchurch Business Park, Ibstone Road, Stokenchurch, HP14 3FE
apmorgan.co.uk	Awais	Ahmad	AP Morgan Limited	12 Church Green East, Redditch, Worcestershire, B98 8BP
cprglobaltech.com	Andrew	Sandbrook	CPR Global Tech Ltd	Unit E2 Lakeside Technology Park, Phoenix Way, Swansea, SA7 9FF
furniss-foods.co.uk	Andrew	Bray	Furniss of Cornwall Limited	Unit 11, Druids Road, Redruth, Cornwall, TR15 3RW
lsa.org.uk	Aaliya	Seyal	Legal Services Agency Limited	Savoy House, 140 Sauchiehall Street, Glasgow, G2 3DH
taylorestates.com	Paul	Taylor	Taylor Estates (UK) Limited	Taylor Business Park, Risley, Warrington, Cheshire, WA3 6BL
thecollectivegroup.co.uk	Jo	Cooper	The Collective Group (Marketing 4 Education Limited)	The Cube, 35 Banbury Road, Nuffield Industrial Estate, Poole, Dorset, BH17 0GA
16i.co.uk	Clare	Partridge	16 Interactive Ltd	6 Rockfield Business Park, Old Station Drive, Cheltenham, Gloucestershire, GL53 0AN
orestonecontrols.co.uk	Warren	Potter	Orestone Controls Limited	Unit 16, High Elms Farm, High Elms Lane, Watford, WD25 0JX
rockallsafety.co.uk	James	Rockall	Rockall Safety Limited	Unit 2, Ocean Way, Ocean Park, Cardiff, CF24 5PG
lambertandfoster.co.uk	Alan	Mummery	Lambert & Foster Limited	77 Commercial Road, Paddock Wood, Tonbridge, Kent, TN12 6DS
dirty-bones.com	Cokey	Sulkin	Dirty Bones Ltd	20-22 Wenlock Road, London, N1 7GU
hydropath.com	Danny	Stefanini	Hydropath Technology Ltd	Unit 2, Bridge Studios, 318-326 Wandsworth Bridge Road, London, SW6 2TZ
sn-group.co.uk	Stuart	Wood	S N Group Limited	Unit 1, Peter Green Way, Barrow-in-Furness, Cumbria LA14 2PE
stok.eu	Frank	Schirrmeister	Arvato SE	Local Court of Gütersloh HRB 11370
terrylifts.co.uk	David	Allen	Terry Group Limited	Unit 1-3, Longridge Trading Estate, Knutsford, Cheshire, UK, WA16 8PR
xytal.com	John	Sneddon	Xytal Limited	Office 7, 35-37 High Street, Barrow-upon-Soar, Loughborough, LE12 8PY
southcroftengineering.co.uk	Andrew	South	Southcroft Engineering Ltd	Thurcroft Industrial Estate, New Orchard Rd, Thurcroft, Rotherham S66 9HY
armonia.co.uk	Diane	Lawrie-Hey	Armonia Limited	Equinox House, Clifton Park, Shipton Road, York, YO30 5PA
creative-bridge.com	Timothy	Perutz	Creative Bridge Ltd	45 Booth Drive, Park Farm Industrial Estate, Wellingborough, NN8 6NL
robotindustrial.co.za	Mark	Jackson	Robot Industrial Supplies (Pty) Ltd	4 Rosslyn Close, Isandovale, Edenvale, Gauteng, 1609, South Africa
andersonacoustics.co.uk	Robin	Monaghan	Anderson Acoustics Limited	Tempus Wharf, 33A Bermondsey Wall West, London, SE16 4ST
exmoortrim.co.uk	Andrew	Horton	Exmoor Trim Limited	Trakkers House, Roughmoor Industrial Estate, Williton, Taunton, TA4 4RF
cedartreehospitality.com	Mohsen	Ghosen	Cedar Tree Hospitality	Al Qusais Industrial 2, 9B Street 23, Dubai, United Arab Emirates
purplespace.org	Brendan	Roach	PURPLESPACE LIMITED	2nd Floor, Here East Press Centre, 14 East Bay Lane, London, E15 2GW
hoge100.co.uk	Stuart	Wild	Hoge 100 Business Systems Ltd	IMS House, Prescott Drive, Worcester, WR4 9NE
careercheck.co.uk	Clive	Jackson	Career Check Limited	Wycliffe House, Water Lane, Wilmslow, Cheshire, SK9 5AF
dysk.co.uk	Timothy	Gurney	Dysk Plc	7 Allied Business Centre, Coldharbour Lane, Harpenden, AL5 4UT
blossomhouseschool.co.uk	Joey	Burgess	Blossom House School Limited	Station Road, Motspur Park, New Malden, KT3 6JJ
ballyhoo-pr.co.uk	Emma	Speirs	Ballyhoo PR	Vulcan Works, 34-42 Guildhall Road, Northampton, NN1 1EW
charnwood-milling.co.uk	Philip	Newton	Charnwood Milling Company Ltd	Saxtead Road, Framlingham, Suffolk, IP13 9PT
argolin.com	Julian	Argolin	Argolin Limited	Longmoor Road, Griggs Green, Liphook, Hampshire, GU30 7PG
booth-ac.com	Gordon	Booth	Booth Air Conditioning Limited	Universal House, Buckley Hill Lane, Milnrow, Rochdale, OL16 4BU
independentlifting.com	Barry	Thompson	Independent Lifting Services Limited	Units 3-4 James Court, Faraday Road, Great Yarmouth, Norfolk, NR31 0NF
beeteealarmsltd.co.uk	Mark	Taylor	Bee Tee Alarms Ltd	176-178 Arkwright Street, Nottingham, NG2 2GD
airstudios.com	Paul	Golding	AIR Studios (Lyndhurst) Ltd	Albany House, Claremont Lane, Esher, Surrey, KT10 9FQ
wymondhamcollege.org	Jonathan	Taylor	Wymondham College (Sapientia Education Trust)	Golf Links Road, Morley St Peter, Wymondham, NR18 9SZ
beckprosper.com	Ian	Griffiths	Beck Prosper Limited	Building 19 First Avenue, The Pensnett Estate, Kingswinford, West Midlands, DY6 7TR
marketingradar.com	Chris	Merrifield	Marketing Radar Ltd	Primrose House, Crawley End, Chrishall, Royston, SG8 8QJ
mtdtraining.co.uk	Sean	McPheat	MTD Training Group Limited	5 Orchard Court, Binley Business Park, Binley, Coventry, CV3 2TQ
kennellaneschool.com	Jennifer	Baker	Kennel Lane School	Kennel Lane, Bracknell, Berkshire, RG42 2EX
climateautogates.co.uk	Peter	Glynn	Climate Autogates	Unit 14, Sawston Trade Park, London Rd, Pampisford, Cambridge, CB22 3EE
mclays.co.uk	Kenneth	Vaughan	McLays (A. McLay & Company Limited)	Longwood Drive, Forest Farm, Cardiff CF14 7ZB
panautos.co.uk	John	Tarbox	Pan Autos (Harpenden) Limited	Unit 1, 48 Coldharbour Lane, Harpenten, Herts, AL5 4UN
sustain-recruitment.com	Steven	Walia	Sustain Recruitment Limited	Lumaneri House Blythe Gate Blythe Valley Park Solihull B90 8AH
faraday-property.com	Aleksandar	Seziner	Faraday Property Management Limited	4th Floor, 20 Red Lion Street, Holborn, London, WC1R 4PS
easthamsandco.co.uk	Matt	Eastham	Easthams & Co (Leaders Limited)	206 Black Bull Lane, Fulwood, Preston, PR2 9XY
priavosecurity.com	Pete	Wilton	Priavo Security Limited	84 Brook Street, Mayfair, London W1K 5EH
itineris.co.uk	Tim	Butcher	Itineris Limited	176-179 Shoreditch High Street, London, E1 6HU
holmeshose.co.uk	Lee	Thomas	Holmes Hose Ltd	Moston Road, Sandbach, Cheshire, CW11 3HL
nationalbusinesscrimesolution.com	Catherine	Bowen	National Business Crime Solution (NBCS)	Regent Centre, Suite 5, Bulman House, Gosforth, Newcastle upon Tyne, NE3 3LS
jmcope.co.uk	Jacob	Cope	Grant Stanley Limited	91 Wimpole Street, London, W1G 0EF
frontech.co.uk	Nirmal	Jain	Frontech Pvt Ltd	Unit-801, EM-4, Sector-V, ECOCENTRE, Kolkata, West Bengal, 700091, India
coastfieldsleisureltd.co.uk	Lloyd	Silvester	Coastfields Leisure Limited	Coastfields Holiday Village, Roman Bank, Vickers Point, Ingoldmells, Skegness, PE25 1JU
alphagrp.co.uk	Robert	Little	Alpha Group (ALPHAGRP LIMITED)	The Water Works, Moors Lane, Great Bentley, Essex, CO7 8QN
baileighindustrial.co.uk	John	Atwell	Baileigh Industrial LTD	Unit D, Swift Point, Swift Valley Industrial Estate, Rugby, Warwickshire, CV21 1QH
emresolutions.com	Christopher	Guerin	EM Resolutions Limited	IC3, Science And Innovation Park, Keele University, Keele, Staffordshire, ST5 5NP
frontstage.co.uk	Christopher	Marshall	Frontstage Furnishing Ltd	Unit 23, Oakfield Business Centre, Stephenson Road, Northacre Industrial Park, Westbury, Wiltshire, BA13 4WF
cosydirect.com	Peter	Ellse	Collaborate & Innovate Ltd (T/A Cosy Direct)	Units 316-318 Fauld Industrial Estate, Fauld Lane, Fauld, DE13 9HS
airseadg.com	Katharine	Staniford	Air Sea Containers Ltd	Staniford Building, 521 Cavendish Street, Birkenhead, CH41 8FZ
bateswharf.co.uk	Richard	Bates	Bates Wharf Marine Sales Ltd	Bridge Wharf, Chertsey, Surrey, KT16 8LG
arka.co	Artan	Sherifi	Arka Design Studio	Canal House, 2 Speirs Wharf, Glasgow, UK, G4 9UG
revolutionfuel.com	John	Sipson	Revolution Fuel (Marine) Limited	Silverstream House, 45 Fitzroy Street, London, W1T 6EB
asiafreightsolutions.co.uk	Steven	Holland	Asia Freight Solutions Ltd	Manchester Business Park, 3000 Aviator Way, Manchester, M22 5TG
hundredhouse.co.uk	Stuart	Phillips	Hundred House Hotel	A442 Bridgnorth Rd, Norton, Telford, TF11 9EE
landoruk.com	Derric	Landor	Landor UK Ltd	51 Clarence Road, Fleet, Hampshire, GU51 3RY
barcadiamedia.co.uk	James	Lucas	Barcadia Media Limited	14 Edward Street, Blackpool, Lancashire, FY1 1BA
andaine.co.uk	Andrew	Evans	Andaine Limited	Central Boulevard, Blythe Valley Business Park, Solihull, B90 8AG
printpallondon.co.uk	Shamir	Parmar	Printpal London (Print Impress Limited)	14 Hendon Lane, Finchley Central, London, N3 1TR
hsil.co.uk	James	Smith	Hull Storage & Interiors Ltd	Taurus House, Valley Way, Kirkella, Hull, HU10 7PW
j-l-a.com	Debbi	Bonner	JLA Communication	The Old Church Business Centre, Quicks Road, London, SW19 1EX, United Kingdom
link-estates.com	Yusuf	Rauf	Link-Estates	Link-Estates, Jantzen House, Ealing Road, Brentford, UK, TW8 0GF
thebirdbath.co.uk	Ian	Taylor	The Bird, Bath	18-19 Pulteney Road (South), Bath, Somerset, BA2 4EZ
quintessenceltd.co.uk	Kanta	Chandarana	Quintessence Ltd	63/66 Hatton Garden, Fifth Floor Suite 23, London, EC1N 8LE
strategy-workshops.co.uk	Roger	Handley	Strategy Workshops	No physical address listed on website (Contact via email only)
elevatedknowledge.co.uk	Lisa	Harris	Elevated Knowledge Ltd	18 Hammond Avenue, Whitehill Industrial Estate, Stockport, SK4 1PQ
feedtheminds.org	Katy	Newell-Jones	Feed the Minds	The Foundry, 17 Oval Way, London, SE11 5RR
islandmeadow.co.uk	Robert	Pratt	Island Meadow Parks (Pratt Developments)	Bracklesham Lane, Bracklesham Bay, Chichester, West Sussex, PO20 8JG
sgs-ltd.com	Zafar	Choudhry	Sentinel Group Security.	36 Oakwood Hill Industrial Estate, Loughton Essex IG10 3TZ
fmiagency.com	Philip	Jones	FMI Agency Limited	101 New Cavendish Street, London, W1W 6XH
carltonlaser.co.uk	Mohan	Jassi	Carlton Laser Services Limited	470 Thurmaston Boulevard, Troon Industrial Estate, Leicester, LE4 9LN
greenboxevents.co.uk	Marcus	Wood	Greenbox Events Ltd	Goldings Heavy Haulage Yard, Charfield Road, Wotton-Under-Edge, GL12 8RL
facewest.co.uk	Trevor	Thompson	Facewest Ltd	Unit 6, Gordon Mill, Netherfield Road, Guiseley, West Yorkshire, LS20 9PD
fleetalliance.co.uk	Andy	Bruce	Fleet Alliance Limited	Skypark 1, 8 Elliot Place, Glasgow, G3 8EP
demack.co.uk	Karen	Richardson	Demack Accountants	124 New Bond Street, London, W1S 1DX
cdsys.co.uk	Simon	Abel	CDS (Fire & Security Solutions)	2 Dominus Way, Meridian Business Park, Leicester, LE19 1RP
gsyseurope.com	Andrew	Bruce	GSYS Limited	Herons Way, Chester Business Park, Chester, CH4 9QR
officegear.co.za	Mark	Joseph	Office Gear	201 Corlett Drive, Bramley, Johannesburg, South Africa
blazenetworks.co.uk	Ben	Brassington	Blaze Networks Ltd	Winterton House, Lyme Green Business Park, Winterton Way, Macclesfield, SK11 0LP
hpruk.com	Iain	Petrie	HPR (UK)	North Office, Lethenty Mill, Inverurie, AB51
salesbond.co.uk	Nicole	Markham	Sales Bond Limited	Unit 1, The Courtyard, Eliot Park, Goldsmith Way, Nuneaton, CV10 7RJ
taskpr.com	Tamara	Kretzer	TASK PR Ltd	96 Great Titchfield Street, London, W1W 6SQ
oxfordchefshop.co.uk	Robert	Maughan	The Oxford Chef Shop	51 Newland Mill, Witney, Oxfordshire, OX28 3SZ
fibox.com	Tapani	Niemi	Fibox Group (HQ)	Keilaranta 17, 02150 Espoo, Finland
kentsavers.co.uk	Ann	Hickey	Wave Community Bank	39-48 Marsham Street, Maidstone, Kent, ME14 1HH
25harleystreet.co.uk	Andrew	Barker	Phoenix Hospital Group	25 Harley Street, London, W1G 9QW
halestooling.com	David	Hales	Hales Tool & Die Ltd	No physical address listed on website (Contact via phone/email)
pps-print.com	Marcus	Swift	PPS Print (Peterborough Printing Services)	Ainsley House, Fengate, Peterborough PE1 5XG
rayflexgroup.co.uk	Phillipa	Taylor	Rayflex Group	Palatine Industrial Estate, Causeway Avenue, Warrington, WA4 6QQ, UK
minutemanbath.co.uk	Nishit	Chotai	Minuteman Press Bath	Unit 2, Pines Way Industrial Estate, Ivo Peters Road, Bath, BA2 3QS
ammerdown.org	Carolyn	Merry	The Ammerdown Centre	Ammerdown Park, Radstock, Somerset, BA3 5SW
moderntelecom.co.uk	Mark	Smedley	Modern Telecom Ltd	Kedleston House, Prime Business Centre, Aspen Drive, Spondon, Derby, DE21 7SS
superfastschools.co.uk	Andrew	Sisson	Superfast Schools (Redraw Internet Ltd)	Trevenson House, Church Road, Pool, Redruth TR15 3PT
hansonmusic.co.uk	Alastair	Hanson	Hanson Musical Instruments	The Old School, 1 Westgate, Honley, Holmfirth, HD9 6AA
rina.org.uk	Paul	Jobson	Royal Institution of Naval Architects	8-9 Northumberland Street, London, WC2N 5DA
kairoswwt.org.uk	Kellie	Ziemba	Kairos Women Working Together	All Saints Church (St Margaret's), 50 Walsgrave Road, CV2 4EB. Our entrance is on Argyll Street
cmsuk.com	Sally	Cross	Corporate Mailing Solutions Ltd	Unit 4b, Chelmsford Road Ind. Estate, Great Dunmow, Essex, CM6 1HD
oversolve.co.uk	Andrew	Bramley	Oversolve Ltd	6-7 Robin Hood St, Nottingham, NG3 1GE
avenium.co.uk	John	Hynes	Avenium Engineering Limited	3A Bowes Road Business Park, Middlesbrough, TS2 1LU
quantumpr.co.uk	Charlie	Vavasour	Quantum Public Relations	Suite 2116 Letraset Building, Wotton Road, Ashford, Kent, TN23 6LN
allsigns.co.uk	Stuart	Turner	Allsigns International Limited	3rd Floor, 207 Regent Street, London, W1B 3HH
coopersoftware.co.uk	Frank	Cooper	Cooper Software Ltd	St Davids House, St Davids Drive, Dalgety Bay, Dunfermline, Fife, KY11 9NB
espstc.com	Steve	Waye	Empowering Strategic Performance Ltd	14 Wellington Business Park, Dukes Ride, Crowthorne, Berkshire, RG45 6LS
sourceqx.com	Richard	Potter	Source (ProtectHear)	18 Eve Street, Louth, Lincolnshire, LN11 0JJ
fireflyfriends.com	Thomas	Babacan	firefly sunrise medical	
anaylin.com	Neal	Rimay-Muranyi	Anaylin Limited	Aston Horsell Way, Woking, Surrey, GU21 4UJ
metalogalva.co.uk				
ddafire.co.uk	David	Conway	DDA Fire Limited	Pinewood Studios, Pinewood Road, Iver Heath, Buckinghamshire, SL0 0NH
reekiesteeltec.com	Derek	McLean	Reekie Steeltec	Baden-Powell Road, Kirkton Industrial Estate, Arbroath, Angus, DD11 3LS
cleanslateltd.com	Mark	Fitzpatrick	Cleanslate Limited	4 Kennet House, 19 High Street, Hungerford, Berkshire, RG17 0NL
printevolved.co.uk	Spencer	Slee	Print Evolved	19 Decimus Park, Kingstanding Way, Tunbridge Wells, TN2 3GP
medialogicdubai.com	Rajesh	Moily	Medialogic Dubai LLC	312, Spectrum Building, Oud Metha, Dubai, United Arab Emirates, P.O.BOX 128059
ppl-cp.com	Andrew	Dawber	Principal Protection Ltd	No physical address listed on website (Headquartered in UK)
morganfuels.com	Hugh	Morgan	Morgan Fuel & Lubes Ltd	254 Dublin Road, Newry, BT35 8RL, United Kingdom
globaltimberproducts.co.uk	Ian	Freeman	Global Timber Products Ltd	Unit 1 Wellington Business Park, New Road, Hixon, Staffordshire, ST18 0HP
manorpackaging.co.uk	David	Orr	Fencor Packaging Group Limited	200 Station Road, Whittlesey, Peterborough, PE7 2HA
raftersrestaurant.co.uk	Alistair	Myers	Rafters Restaurant	220 Oakbrook Road, Sheffield, S11 7ED
berkshireaesthetics.com	Selena	Langdon	Berkshire Aesthetics	Furze Platt Road, Maidenhead, SL6 6PR
dkhughes.co.uk	Dean	Hughes	D K Hughes Limited	Unit 3, Block C The Courts, Kestrel Road Trafford Park Manchester, M17 1SF
diplomatsofsound.org	Si	Chai	Diplomats of Sound	4 Campbell Court, Bristol, BS11 0LF, United Kingdom
imprimatur.co.uk	Nicola	Humphreys	Imprimatur Services Limited	Soho 13 20 Ingestre Place London W1F 0DS, England
gkandnservices.co.uk	Gary	Crossland	G K & N Services Limited	Unit 6/7 Lee Mills Parkside, Scholes, Holmfirth, HD9 1RT
speedwaydelhi.com	Vipan	Pahwa	Speedway Surgical Co.	A-67/5, GT Karnal Road Industrial Area, Delhi-33, India
cdpltd.co.uk	Ilya	Alshine	Cloud Data Protection Ltd	167 - 169 Great Portland Street, 5th Floor, London, W1W 5PF
teisenproducts.com	Andrew	Teisen	Teisen Products Ltd	Bradley Green, Worcestershire, B96 6RP
pro-roll.co.uk	Caroline	Havenhand	Pro-Roll Ltd	Pluto Works, Penistone Road North, Sheffield, S6 1LP
novus-med.com	Andrew	James	Novus Med	1110 Elliott Court, Coventry Business Park, Herald Avenue, Coventry, West Midlands, CV5 6UB, UK
sueyatespersonnel.com	Sue	Yates	Sue Yates Personnel Services	Marston House, 5 Elmdon Lane, Marston Green, Solihull, West Midlands B37 7DL, GB
excelsiorscientific.com	Jason	Goodall	Excelsior Scientific Ltd	Unit 28C Europa Way, Wisbech, PE13 2TZ
duracelldirect.co.uk	James	McBrien	PSA Parts Ltd (T/A Duracell Direct)	2 Prince Georges Road, Colliers Wood, London, SW19 2PX
classicbritain.com	Mark	Simpson	Classic Britain	3 Dunlop Street, Strathaven, ML10 6LA
ak-wells.com	Stewart	Adams	AK Well Services Limited	Westhill Business Centre, Endeavour Drive, Westhill, Aberdeen, AB32 6UF
skoutpr.com	Rob	Skinner	Skout Public Relations Ltd	11 Marketplace, Macclesfield, SK10 1EB
brillopak.co.uk	Peter	Newman	Brillopak Ltd	9 Archers Park, Branbridges Road, Tonbridge, Kent, TN12 5HP
heritagecollective.co.uk	Danielle	Morgan	Heritage Collective	Stanley Building, 7 Pancras Square, London N1C 4AG, United Kingdom
jespers.co.uk	Lynn	Cummings	Jespers of Harrogate	14 Oxford Street, Harrogate, North Yorkshire, HG1 1PU
technologynetworks.com	Robert	Kafato	Technology Networks Limited	Woodview, Bull Lane, Sudbury, Suffolk, CO10 0FD
treewisesolutions.co.uk	Alastair	Sisson	Tree Wise Solutions Ltd	Moorhouse Courtyard, Warwick on Eden, Cumbria CA4 8PA
burkeandwills.co.uk	Mark	Burke	Burke & Wills Removals Ltd	42 Portslade Rd, Battersea, London, SW8 3DH
controlledspace.co.uk	Steven	Johnson	Controlled Space Limited	Unit 4, The Courtyards, 110-118 Church Street, Leeds, LS10 2JA
thebrightmediaagency.com	David	Shaw	The Bright Media Agency Limited	The Stables, Dovecote Court, Pingle Lane, Potters Marston, LE9 3JR
fieldworkhub.com	Iain	Johnston	FieldworkHub Ltd	131 Finsbury Pavement, London, EC2A 1NT
atlasmarine.sg	Stephen	Herron	Atlas Marine Services Pte Ltd	51 Bukit Batok Crescent, #03-12/13 Unity Centre, Singapore 658077
thecablenet.net	Nick	Dykins	Slingco Limited (T/A Cablenet)	New Hall Hey Road, Rawtenstall, BB4 6JG, England
gascoyne.org	Jorge	Mendonça	Gascoyne Estates Limited	Hatfield Park Estate Office, The Melon Ground, Hatfield, Hertfordshire, AL9 5NB
pixfizz.com	Jeremy	Hyams	Pixfizz	No physical address listed on website (UK incorporated)
keyphoto.com	Gary	Walker	Key Portfolio	No physical address listed on website (Contact via online form)
8point8training.com	Sam	Goundry	8point8 Training Limited	Unit 11, Yorkshire Way, Armthorpe, Doncaster, South Yorkshire, DN3 3FB
thefirebeamcompany.com	John	Davies	The Fire Beam Company Limited	200 Capability Green, Luton, Bedfordshire, LU1 3LU
winchmorelimited.co.uk	David	Rutter	Winchmore Limited	403 High Road, Woodford Green, Essex, IG8 0XG
rgssheetmetal.co.uk	John	Craig	RGS Sheetmetal Limited	Units 8, 9, 10 & 12 Forbes Court, Billington Road Industrial Estate, Burnley, Lancashire, BB11 5UB
airpart.co.uk	David	McHugh	Airpart Supply Ltd	Unit 3, The Gateway Centre, Coronation Road, Cressex Business Park, High Wycombe, Buckinghamshire, HP12 3SU
fuelactive.com	Max	Lytle	FuelActive Ltd	Unit 2, Glan-Y-Llyn Industrial Estate, Cardiff Road, Taff's Well, Cardiff, CF15 7JD
theoraclegroup.co.uk	Caroline	Coskry	The Oracle Group	Global House, Ashley Avenue, Epsom, Surrey, KT18 5AD
engagecf.co.uk	Oliver	Deed	Forestville Communications Ltd (T/A ECF)	The Stanley Building, 7 Pancras Square, London N1C 4AG
skylinewhitespace.com	Mary	Cole	Whitespace Exhibitions Ltd (T/A Skyline Whitespace)	320 Western Road, London, SW19 2QA
hamptonclinic.co.uk	Lorraine	Hill	Hampton Clinic	14 Station Road, Knowle, Solihull, B93 0HT
noxboxltd.com	Jason	Aexel	NOxBOX Ltd	Unit 1, Eurolink Gateway, Castle Road, Sittingbourne, Kent, ME10 3AG
efspecialists.co.uk	Stephen	Wilson	Environmental Filtration Specialists Ltd	Unit 3, Waverley Industrial Estate, Bathgate, West Lothian, EH48 4JA
cotherm.co.uk	Paul	Morgan	Cotherm (UK) Limited	107 traverse des levées, Parc d'activité Les Levées, 38470 Vinay – France
platform81.com	Gary	Mawhinney	Platform81	399 Didsbury Road, Heaton Mersey, Stockport, SK4 3HB
caloo.co.uk	Geoffrey	Rodwell	Caloo Ltd	Unit 9A, Triangle Business Park, Wendover Road, Stoke Mandeville, HP22 5BL
nemein.co.uk	Suzannah	Bourne	Nemein Ltd	4 Squire Drive, Brynmenyn Industrial Estate, Bridgend, CF32 9TX
in2events.co.uk	Ryan	Crowder	In 2 Events Limited	1 Silverthorne Way, Waterlooville, Hampshire, PO7 7XB
ajcockerassociates.co.uk	Ian	Stott	A J Cocker Associates	New Century House, 176 Drake Street, Rochdale, Lancashire, OL16 1UP
rovtechsolutions.co.uk	John	Polson	Rovtech Solutions Ltd	Unit 16, Andrews Court, Andrews Way, Barrow-in-Furness, LA14 2UE
westerton.com	Robin	Porter	Westerton Access Limited	Norsea House, Crawpeel Road, Altens Industrial Estate, Aberdeen, AB12 3LG
aprao.com	Daniel	Norman	Aprao Limited	1 New Fetter Lane, London, EC4A 1AN
alltechsigns.com	David	Bangs	Alltech Signs & Graphics Ltd	Unit 14 Firbank Way, Leighton Buzzard, Bedfordshire, LU7 4YP
completewashroomsolutions.co.uk	Timothy	Doyle	Complete Washroom Solutions Limited	91 Main Rd, Meriden, Coventry CV7 7NL, United Kingdom
integratechnical.com	Ewan	Cresswell	Integra Technical Services (ITS) UK Ltd	1st Floor, Sackville House, 143-149 Fenchurch Street, London, EC3M 6BN
kl-communications.com	Jamie	Legg	Kaso Legg Communications Limited	Kaso Legg Communications, 40 Queen Street. London, EC4R 1DD
greatlandgold.com	Shaun	Day	Greatland LTD	Level 2, 502 Hay St, Subiaco, Western Australia 6008
westsell.co.uk	Dale	Cheasley	Westsell Ltd	The Old Quarry, Emborough, Somerset, BA3 4SD
cbcontracts.com	Colin	Bunting	CB Contracts (NI) Ltd	Unit B1, 52 Sydenham Business Park, 19 Heron Road, Belfast, BT3 9LE
thepdgroup.com	Clive	Stewart	The PD Group Ltd	Never Despair Studios, Unit 2, Alton Road, South Warnborough, Hook, RG29 1RT
dearnefm.co.uk	Yvonne	Bauer	Dearne FM Limited	The Lantern, 75 Hampstead Road, London NW1 2PL
fifthst.co.uk	Margaret	Baldwin	Fifthstreet Management Limited	Kingston House North, Princes Gate, London, SW7 1LN
marshallacm.co.uk	Sion	Lewis	Ciphr Limited.	Reg Office: 3rd Floor, 33 Blagrave Street, Reading, RG1 1PW
libertinelondon.com	Shirley	Buttons	Libertine London Ltd	21 Tower Street, London, WC2H 9NS
heartvets.co.uk	David	Dickson	HeartVet Consultants Ltd	Waldenfields, Whitestone, Exeter, EX4 2HP
blacklinesafety.com	Cody	Slater	Blackline Safety Corp.	800, 808 4 Avenue SW, Calgary, Alberta, T2P 3E8, Canada
baumanlyons.co.uk	Christopher	Smith	Bauman Lyons Architects Ltd	Black Building, 2 Newton Road, Leeds, LS7 4HE
purerenewables.co.uk	Christopher	Whitelock	Pure Solar Ltd (T/A Pure Renewables)	14D iPark Industrial Estate, Innovation Drive, Hull, HU5 1SG
interdirect.co.uk	Nicholas	Mann	Interdirect Limited	289 Upper Fourth Street, Milton Keynes, Buckinghamshire, MK9 1EH
thistledecorators.co.uk	Mark	Ivinson	Thistle Decorating Services Limited	22-26 Academy Street, Leith, Edinburgh, EH6 7EF
northwestchoirs.org	Lori	Conzatti	North West Choirs	5031 University Way NE, #NB2, Seattle, WA 98105
sketchleygrangehotel.co.uk	Mohammad	Gokal	Sketchley Grange Hotel	Sketchley Lane, Burbage, Hinckley, Leicestershire, LE17 3HU
d-sankey.co.uk	David	Sankey	Capital Pest Control	39 Sackville Road, BN3 3WD
i-teach.org.uk	Andrew	Rosser	iTeach (Wales) Limited	Ocean Park House, East Tyndall Street, Cardiff, CF24 5ET
h-m.co.uk	Peter	McNulty	Hammond McNulty LLP	Bank House, Market Square, Congleton, Cheshire, CW12 1ET
castlecartons.co.uk	James	Green	Castle Cartons Limited	96-112 Kings Road, Kings Heath, Birmingham, B14 6TN
meninshedsmk.org.uk	Michael	West	Men in Sheds Milton Keynes	30 Burners Lane, Milton Keynes, MK11 3HE
eaglefabs.co.uk	Josh	Holloway	Eagle (G.E.T.) Fabrications Ltd	2 Kett St, Nottingham, NG6 8NX
superglazed.co.uk	Nalini	Patel	Superglazed Ltd	Unit 9 & 10 Genesis Business Park, Rainsford Road, Park Royal, London, NW10 7RG
rogue-resolutions.com	Andrew	Thomas	Brainbox Ltd	6 Museum Place, Cardiff CF10 3BG, United Kingdom
duffyrafferty.com	Lawrence	Duffy	Duffy Rafferty Communications	18 Heron Road, Sydenham Business Park, Belfast, BT3 9LE
mauriceflynn.com	Aidan	Flynn	Maurice Flynn & Sons Ltd	Saunders House, 2 Springbank Road, Dunmurry, Belfast, BT17 0QL
sdsdrives.com	Vina	Panchal	SDS Limited	Unit 6, St Martin's Park, Moorend Farm Avenue, Avonmouth, Bristol, BS11 0RS
tubzbrands.co.uk	Simon	Smith	Tubz Brands Group	Unit 3 Eurolink Gateway, Sittingbourne, Kent ME10 3AG
impactcoatings.co.uk	Perry	Watson	Impact Coatings	Unit F, Global Park, Moorside, Colchester, Essex, CO1 2TJ
quorumprint.co.uk	Peter	Minnis	Quorum Print Services Ltd	BizSpace Gloucester, Corinium House, Corinium Avenue, Barnwood, Gloucester GL4 3HX
harmill.co.uk	Patrick	Hughes	Harmill Systems Ltd	Unit P Cherrycourt Way, Leighton Buzzard LU7 4UH, UK
silverstream-tech.com	Noah	Silberschmidt	Silverstream Technologies	1 St Vincent Street, London, W1U 4DA
kdmediapublishing.com	Sarah	Ellis	Ellis Media and Events Ltd	Pantile House, Newlands Drive, Witham, Essex, CM8 2AP
csl-engineering.com	Mons	Aase	DOF Subsea	Horizons House, 81-83 Waterloo Quay, Aberdeen AB11 5DE, United Kingdom
vinteclabs.com	Andrew	Stirrat	Vintec Laboratories Ltd	Building 26, BRE, Bucknall Lane, Watford, WD25 9XX
fourjays.co.uk	Nathan	Heathcote	Four Jays Group	Barling Farm, East Sutton, Maidstone, Kent, ME17 3DX
hitachirail.com	Giuseppe	Marino	Hitachi Rail Limited	7th Floor, 60 Ludgate Hill, London, EC4M 7AW
minteg.co.uk	Tyson	deSouza	MInteg Limited	Howes Road, Aberdeen, AB16 7AG
wrt.org.uk	Laurence	Couldrick	Westcountry Rivers Trust	Rain-Charm House, Kyl Cober Parc, PL17 8PH
securityandeventsolutions.co.uk	Gareth	Gwynne-Smith	Security and Event Solutions Ltd	59 North Street, Portslade, Brighton, BN41 1DH
sourcing.co.uk	Gill	Thorpe	The Sourcing Team Ltd	8 The Parade, Stafford Rd, Wallington, SM6 8ND
aquaterra.co.uk	Stephen	Taylor	AquaTerra Group Ltd	AquaTerra House, Tofthills Avenue, Aberdeen, AB51 0QP
drewry.co.uk	Tim	Power	Drewry Shipping Consultants Ltd	35-41 Folgate Street, London, E1 6BX
weareyellowball.com	Owen	Hunnam	Yellowball	Borough Yards, 13 Dirty Lane, London, SE1 9PA
vistechcooling.co.uk	Martin	Crunden	Vistech Cooling Systems Ltd	Unit 1, Blackhouse Farm, Blackhouse Road, RH13 6HS
avs-uk.co.uk	Ian	Baker	Associated Vending Services Ltd	Unit 10, Tame Valley Business Centre, Tamworth, B77 5BY
primaryt.co.uk	Daniel	Toon	Primary Technology	Primary Technology Ltd, 4 Legrams Terrace, Fieldhead Business Centre, Bradford, West Yorkshire, BD7 1LN
herbsinabottle.com	Yvonne	Bishop-Weston	Herbs in a Bottle Ltd	C/O The Robert Edwards Partnership, 1 Bentinck Street, London, W1U 2ED, UK.
911-recovery.com	James	Sneddon	911 Rescue recovery Limited	2 Jessie Street, Polmadie, Glasgow, G42 OPG
helicentre.com	Chris	Line	Helicentre Aviation Ltd	Business Aviation Centre, Viscount Drive, Liverpool John Lennon Airport, Merseyside, L24 5GA
becservices.co.uk	Clive	Elsworth	B E C Services	260-262 Ringwood Road, Parkstone, Poole, BH14 0RS
andrewmorrisgolf.com	Andrew	Morris	Andrew Morris Golf	24 Ballyskeagh Road, Lisburn, Co. Down, BT27 5SY, Northern Ireland
richardrussell.co.uk	Richard	Russell	Richard Russell (Panels) Ltd	Units 1 – 3, Beddington Trading Park, Bath House Road, Croydon, Surrey, CR0 4TT
sentinelmanufacturing.co.uk	Georgia	Baker	Sentinel Manufacturing Ltd	March Way, Battlefield Enterprise Park, Shrewsbury, SY1 3JE
firma-chrome.co.uk	Andrew	Bramley	Firma-Chrome Ltd	Soho Works, Saxon Road, Sheffield, S8 0XZ
trendtype.com	Benjamin	Seeley	Trendtype	Impact Brixton, 17A Electric Lane, London, SW9 8LA
eightandfour.com	Kate	Ross	Eight&Four Group	1st Floor, White Collar Factory, London, EC1Y 8AF
noisesolutions.co.uk	Dean	Bowden	Noise Solutions Ltd	Unit 5 Oriel Court, Omega Park, Alton, GU34 2YT
gbruce.co.uk	Mark	Armstrong	G. Bruce & Co Ltd (Brusco Food Group)	Suite 3A Haddonsacre, Station Road, Offenham, Evesham, WR11 8JJ
modaliving.com	Johnny	Caddick	Moda Living Ltd	Central House, Beckwith Knowle, Otley Road, Harrogate, HG3 1UG
notusheavylift.com	Stewart	Kay	Notus Heavy Lift Solutions Ltd	Sovereign Chambers, 3 Temple Square, Liverpool, L2 5BA
bentleysecurity.com	Nicola	Mcgreavey	Bentley Security Projects Ltd	Dickinson Street, Oldham, OL4 1HD
flu-xpress.co.uk	Julian	Evans	Flu Xpress Ltd	893 Plymouth Road, Slough, Berkshire, SL1 4LP
solidpoint.co.uk	James	Snelgrove	SolidPoint Limited	2 Wentworth House, Vernongate, Derby, DE1 1UR
logic4training.co.uk	Kevin	Budd	Gas Logic Ltd	Unit 7 Belvue Business Centre, Belvue Road, Northolt, UB5 5QQ
mdd.org.uk	John	Burnside	MD Diagnostics Ltd	Slip 7 Annexe, The Historic Dockyard, Chatham, Kent, ME4 4TZ
elmhirstparker.com	Martin	Legg	Elmhirst Parker LLP	17-19 Regent Street, Barnsley, South Yorkshire, S70 2HP
pearcommunications.co.uk	Eduardo	Stevens	Pear Communications Ltd	Arundel House, 1 Amberley Court, Whitworth Road, Crawley, RH11 7XL
clevedongolfclub.co.uk	Karen	Drake	Clevedon Golf Club	Castle Road, Clevedon, Somerset, BS21 7AA
ideas4careers.co.uk	Michelle	Taylor	Ideas4Careers (UK) Ltd	Ideas4Careers (UK) Ltd, 18 Oxbury Road, Watnall, Nottingham, NG16 1JP
deuco.co.uk	Graham	Wickens	Deuco Bathroom Furniture Limited	10 Sybron Way, Millbrook Industrial Estate, Crowborough, East Sussex, TN6 3DZ
dovedavies.com	Fraser	Crichton	Dove Davies and Partners	9-11 Atholl Place, Edinburgh, EH3 8HP
almasam.ae	Azam	Kashmiri	Al Masam Stationery L.L.C	Lahej Khalifa Al Basti Building, Shop# 1 & 2, Zabeel Street, near Karama GPO, Dubai, UAE
avenuecareservices.co.uk	Ian	Campbell	Avenue Care Services Ltd	18a Dickson Street, Dunfermline, Fife, KY12 7SL
bjb-windows.co.uk	David	Jones	BJB Windows	Guildford Road, Normandy, Guildford, Surrey, GU3 2AU
theredbrickroad.com	Richard	Megson	The Red Brick Road Ltd	366 Gray's Inn Road, London, WC1X 8BE
vem.co.uk	Daniel	Kottow	Vibrant Energy Matters Limited	2 Foxes Lane, Oakdale Business Park, Blackwood, Gwent, NP12 4AB
normie.co.uk	Josh	Gertler	Normie & Co	503-505 Bury New Road, Prestwich, Manchester M25 1AD
jlfmovingsolutions.co.uk	Jacob	Corlett	JLF Moving Solutions Ltd	Unit 4, Kingsdown Orchard, Rowden Lane, Blunsdon, Swindon, SN26 7RR
academyinsurance.co.uk	Gordon	Crosbie	Academy Insurance Services Limited	Davidson House, Forbury Square, Reading, RG1 3EU, United Kingdom.
hawksightsrm.com	Paul	Mercer	Hawksight SRM	Apartment 79 Chatham House, Racecourse Road, Newbury, Berkshire, England, RG14 7GJ
echostudios.co.uk	Mark	Cardwell	Echo Studios	Red Lion Business Park, Surbiton, KT6 7RD
bw-industries.co.uk	Gareth	Rounding	B W Industries Ltd	Jensen House, Carnaby Industrial Estate, Bridlington, East Yorkshire, YO15 3QY
strategyinternational.co.uk	Robin	MacKenzie	Strategy International	40-44 Newman Street, London, W1T 1QD
magpie-security.co.uk	Jason	Bailey	Magpie Security Ltd	A3 Poulton Drive, Nottingham, NG2 4BN
empire-estates.com	Akber	Ali	Empire Estates	12-14 High Road, Willesden Green, London, NW10 2QG
cashconverters.co.uk	Carl	Murray	Cash Converters (UK) Limited	Artisan Hillbottom Road, Sands Industrial Estate, High Wycombe, HP12 4HJ
virginincentives.co.uk	Danni	Rush	Virgin Incentives	Stamford House, Boston Drive, Bourne End, Buckinghamshire, SL8 5YS
itfocus-tm.com	James	Abbott	IT Focus Telemarketing Ltd	Treenwood House, Rowden Lane, Bradford on Avon, BA15 2AU
tampopo.co.uk	David	Fox	Tampopo Ltd	Albert Square, Manchester, M2 5PF
interceramica.co.uk	Rebecca	Challis	Inter Ceramica Limited	Unit 13A, Hornbeam Park Oval, Hornbeam Park, Harrogate, HG2 8RB
octopus-res.co.uk	Phillip	Knowles	Octopus Residential Limited	227 Chapeltown Road, Leeds, West Yorkshire, LS7 3DX
carnabyerp.com	Kelvin	Forrester	Carnaby Associates Ltd (T/A CarnabyERP)	48 Warwick Street, London, W1B 5AW
airmtm.com	Tim	Parsa	AirMTM Limited	11 Raven Wharf, 14 Lafone Street, London, SE1 2LR
clancy.co.uk	Nick	Riding	Clancy Consulting Limited	4th Floor, Windmill Green, 24 Mount Street, Manchester, M2 3NX
veracityglobal.com	Alastair	McLeod	Veracity UK Ltd	4 Dow Road, Prestwick International Aerospace Park, Prestwick, KA9 2TU
"""

def load_cache():
    """Load existing learning cache"""
    if os.path.exists(LEARNING_CACHE_FILE):
        with open(LEARNING_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save learning cache"""
    with open(LEARNING_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def add_verified_data():
    """Add verified data to learning cache with 1.0 confidence"""
    cache = load_cache()
    
    lines = VERIFIED_DATA.strip().split('\n')
    added = 0
    skipped = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split('\t')
        if len(parts) < 5:
            skipped += 1
            continue
            
        domain = parts[0].strip()
        first_name = parts[1].strip() if len(parts) > 1 else ""
        last_name = parts[2].strip() if len(parts) > 2 else ""
        company_name = parts[3].strip() if len(parts) > 3 else ""
        address = parts[4].strip() if len(parts) > 4 else ""
        
        # Skip if no valid domain or company name
        if not domain or not company_name:
            skipped += 1
            continue
            
        # Combine first and last name for officer
        officer = f"{first_name} {last_name}".strip() if first_name and last_name else ""
        
        # Create cache entry with 1.0 confidence
        cache[domain] = {
            "candidates": {
                "company_name": {
                    "value": company_name,
                    "confidence": 1.0,
                    "source": "ManualVerified"
                },
                "address": {
                    "value": address,
                    "confidence": 1.0,
                    "source": "ManualVerified"
                },
                "officer": {
                    "value": officer,
                    "confidence": 1.0,
                    "source": "ManualVerified"
                }
            },
            "validated": True,
            "user_corrected": True,
            "updated_at": datetime.now().isoformat()
        }
        added += 1
    
    save_cache(cache)
    print(f"Added {added} verified entries to learning cache")
    print(f"Skipped {skipped} invalid entries")

if __name__ == "__main__":
    add_verified_data()

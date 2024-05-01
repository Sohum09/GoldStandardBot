import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents = intents)

@bot.event
async def on_ready():
    print(f'Bot is ready! logged in as TestingDaBot#0852')
    print(f'Connected to {len(bot.guilds)} server(s)')
    await bot.change_presence(activity=discord.Game(name="IBTRACS, OISST, ERSST, ONI, MEI, IOD, and SMAP Databases."))
    # Print the names of each server
    print('Connected to servers:')
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id})')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Type `!commandHelp` for a list of commands.")
    else:
        await ctx.send(f"An error occurred: {error}")


@bot.command(name='hi', help='Send a message that says hi!')
async def hi(ctx):
    print("Command received!")
    await ctx.send('Hello, this is the GoldStandardBot!')

@bot.command(name='respond', help='Send a message that says hi!')
async def respond(ctx):
    print("Command received!")
    await ctx.send('You guys need to chill')

@bot.command(name='atcf', help='Display ATCF and decode it')
async def atcf(ctx, info=""):
    import urllib3
    from bs4 import BeautifulSoup

    # Step 1: As the ATCF URL has a bugged SSL certificate, the following workarounds are needed: 
    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Explicitly disable SSL verification
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    
    # URL of the ATCF data
    atcf_url = 'https://www.nrlmry.navy.mil/tcdat/sectors/atcf_sector_file'

    # Step 2: Fetch ATCF data:
    def fetch_atcf_data(url):
        response = http.request('GET', url)
        return response.data.decode('utf-8')

    # Step 3: Display the ATCF data: 
    def parse_atcf_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    # Step 4: Fetch and parse ATCF data
    atcf_data = fetch_atcf_data(atcf_url)
    parsed_data = parse_atcf_data(atcf_data)

    # Step 5: Display the parsed data in encoded format:
    if parsed_data == '':
        await ctx.send(f"```No storms are active.```")
    else:
        await ctx.send(f"```{parsed_data}```")

    # Step 6: We will now display the data by decoding it:
    def displayStormInfo(storm_data):
        result = ""
        result += "\nDecoded information from the ATCF: \n"
        basin_list = {
            'L': "North Atlantic Ocean", 
            'E': "East Pacific Ocean", 
            'C': "Central Pacific Ocean", 
            'W': "Western Pacific Ocean", 
            'A': "Arabian Sea",
            'B': "Bay of Bengal",
            'S': "South Indian Ocean",
            'P': "South Pacific Ocean"
        }
        #Helper function that finds the status of the storm...
        def designation(basin, winds):
            winds = int(winds)
            status = ""
            if winds >= 130 and basin == 'W':
                status = "Super Typhoon"
            elif winds >= 100:
                if (basin == 'L' or basin == 'E' or basin == 'C'):
                    status = "Major Hurricane"
                elif basin == 'W':
                    status = "Major Typhoon"
                else:
                    status = "Major Cyclone"
            elif winds >= 65:
                if (basin == 'L' or basin == 'E' or basin == 'C'):
                    status = "Hurricane"
                elif basin == 'W':
                    status = "Typhoon"
                else:
                    status = "Cyclone"
            elif winds >= 50 and (basin == 'W' or basin == 'S'):
                status = "Severe Tropical Storm"
            elif winds >= 35:
                status = "Tropical Storm"
            elif winds >= 25:
                status = "Tropical Depression (Autoflagged)"
            else:
                status = "Tropical Low"
            return status

        for storm in storm_data:
            result +=f"\n```Storm ID: {storm['atcf_id']}"
            result +=f"\nName of Storm: {designation(storm['atcf_id'][-1], storm['winds'])} {storm['name']}"
            result +=f"\nDate of Reading: {storm['date']}"
            result +=f"\nTime of Reading: {storm['hour']} UTC"
            result +=f"\nCoordinates: {storm['latitude']}, {storm['longitude']}"
            result +=f"\nBasin: {storm['basin']} - {basin_list[storm['atcf_id'][-1]]}"
            result +=f"\nIntensity: {storm['winds']} Kts / {storm['pressure']} hPa```"
        return result

    #Step 7: To allow the function in Step 6 to work, we will now work on decoding the ATCF data:
    storm_data = []
    lines = parsed_data.split('\n')

    for line in lines:
        if line.strip():
            parts = line.split(' ')
            storm_data.append({
                'atcf_id': parts[0],
                'name': parts[1],
                'date': f"{parts[2][4:]}-{parts[2][2:4]}-{parts[2][:2]}",
                'hour': parts[3],
                'latitude': parts[4],
                'longitude': parts[5],
                'basin': parts[6],
                'winds': parts[7],
                'pressure': parts[8]
            })

    #Step 8: We conclude Steps 6 and 7 to display the decoded data:
    if info != "":
        res = displayStormInfo(storm_data)
        await ctx.send(res)


@bot.command(name='btk', help='Get data on the most recent storms')
async def btk(ctx, btkID:str, yr:str):
    import urllib3
    from bs4 import BeautifulSoup

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    btkID = btkID.lower()

    if btkID[:2] in ['sh', 'wp', 'io']:
        btkUrl = f'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/JTWC/b{btkID}{yr}.dat'
    else:
        btkUrl = f'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/NHC/b{btkID}{yr}.dat'
    await ctx.send(btkUrl)
    btk_data = fetch_url(btkUrl)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')

    btk_parameters = lines[-2].split(',')
    bt_list = []
    for i in range(len(btk_parameters)):
        bt_list.append(btk_parameters[i].strip())

    def calc_ACE(btkLines):
        ace = 0
        for line in btkLines:
            if line.strip():
                params = line.split(',')
                if(params[11].strip() == '34'):
                    ace += (int(params[8]) ** 2) / 10000
        return "{:.4f}".format(ace)

    res = ""

    def decode_JTWC_btk(bt_list):
        coord_x = bt_list[6][:-2] + "." + bt_list[6][-2:]
        coord_y = bt_list[7][:-2] + "." + bt_list[7][-2:]
        result = ""
        result +=f"```ATCF ID: {bt_list[0]}{bt_list[1]}{yr}"
        result +=f"\nName of Storm: {bt_list[10]} {bt_list[27]}"
        result +=f"\nTime and Date: {bt_list[2][8:]}00 UTC, {bt_list[2][6:8]}/{bt_list[2][4:6]}/{bt_list[2][:4]}"
        result +=f"\nCoordinates of center: {coord_x}, {coord_y}"
        result +=f"\n\nCurrent Intensity: {bt_list[8]} Kts, {bt_list[9]} hPa"
        result +=f"\nCurrent ACE upto this point: {calc_ACE(lines)}"
        result +=f"\nENVP: {bt_list[17]} hPa"
        result +=f"\nROCI: {bt_list[18]} nm"
        result +=f"\nRMW: {bt_list[19]} nm```"
        return result

    res = decode_JTWC_btk(bt_list)
    await ctx.send(res)

@bot.command(name='ripa')
async def ripa(ctx, btkID:str):
    import urllib3
    import requests
    from bs4 import BeautifulSoup
    import os
    from datetime import datetime

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    current_datetime = datetime.now()
    year = str(current_datetime.year)
    month = str(current_datetime.month).zfill(2)
    day = str(current_datetime.day).zfill(2)
    hourInt = 18
    btkID = btkID.lower()
    btkUrl = f"https://rammb-data.cira.colostate.edu/tc_realtime/products/storms/{year}{btkID}/ripastbl/{year}{btkID}_ripastbl_{year}{month}{day}{str(hourInt).zfill(2)}00.txt"

    while hourInt >= 0:
        response = requests.get(btkUrl)
        if response.status_code != 200:
            hourInt -= 6
            btkUrl = f"https://rammb-data.cira.colostate.edu/tc_realtime/products/storms/{year}{btkID}/ripastbl/{year}{btkID}_ripastbl_{year}{month}{day}{str(hourInt).zfill(2)}00.txt"
        else:
            break
    print(btkUrl)
    
    btk_data = fetch_url(btkUrl)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')
    await ctx.send("Hold as the file is generated.")
    
    # Write the results to a text file
    output_file_path = "ripa_table_results.txt"
    with open(output_file_path, "w") as output_file:
        for line in lines:
            if line.strip():
                output_file.write(line + "\n")
    
    # Send the text file as an attachment
    with open(output_file_path, "rb") as output_file:
        await ctx.send(file=discord.File(output_file))

    # Delete the temporary text file
    os.remove(output_file_path)



@bot.command(name='amsu')
async def amsu(ctx, header:str):
    import urllib3
    from bs4 import BeautifulSoup

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()
    
    header = header.upper()
    btkUrl = f'https://tropic.ssec.wisc.edu/real-time/amsu/archive/2024/2024{header}/intensity.txt'

    btk_data = fetch_url(btkUrl)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')
    res = "```"
    for line in lines:
        res += line + "\n"
    res += '```'
    await ctx.send(res)



@bot.command(name='ckz', help='Calculate the ckz WP relationship')
async def ckz(ctx, vmax:float, storm_movement:float, latitude:float, roci:float, envp:float):
    import numpy as np
    latitude = abs(latitude)
    #Velocity of storm with respect to movement speed:
    vsrm1 = vmax - 1.5 * (storm_movement ** 0.63)
    envp = envp+2
    #S = Storm size factor that is used to adjust the pressure.

    #1.ROCI
    S_ROCI = (roci/60)/8 + 0.1
    if(S_ROCI < 0.4):
        S_ROCI = 0.4
  

    #From here, we split the formula in two....
    def Pc(V,S,L,P):
        if (latitude <= 18):
            pc = 5.962 - 0.267*V - (V/18.26)**2 - 6.8*S + P
            #Case 1, we typically reduce the importance of latitude in the formula...
        else:
            pc = 23.286 - 0.483*V - (V/24.254)**2 - 12.587*S - 0.483*L + P
        return(pc)

    #We then display the result in an easy to read manner...
    Pc_ROCI = round(Pc(vsrm1,S_ROCI,latitude,envp), 2)
    await ctx.send(f"CKZ Result (ROCI): {vmax} kt, {Pc_ROCI} mb")

@bot.command(name='rev_ckz', help='Calculate the reverse of the ckz WP relationship')
async def rev_ckz(ctx, pres:float, storm_movement:float, latitude:float, roci:float, envp:float):
    import numpy as np
    import math
    latitude = abs(latitude)
    poci = pres - 2

    #S-ratio calculation...
    S = (roci/60)/8 + 0.1
    if(S < 0.4):
        S = 0.4

    delP = abs(poci - envp)

    #Implementing reverse CKZ equation from KZ et al. 2007:
    vmax = 18.633 - 14.690 * S - 0.755 * latitude - 0.518 * (poci - envp) + 9.378 * math.sqrt(delP) + 1.5 * storm_movement ** 0.63

    #Make the output a little presentable:
    vmax = "{:.2f}".format(vmax)
    await ctx.send(f"Output winds: {vmax} kt")

@bot.command(name='messup')
async def messup(ctx):
    await ctx.send("The creator of this bot has made a terrible mistake and is currently reflecting on his life choices while rectifying it.")

@bot.command(name='ah77')
async def ah77(ctx, vmax:float):
    pc = 1010 - (vmax/6.7) ** (1/0.644)
    pc = "{:.2f}".format(pc)
    await ctx.send(f"Output in AH77: {pc} hPa")

@bot.command(name='rev_ah77')
async def rev_ah77(ctx, pc:float):
    vmax = 6.7 * (1010 - pc) ** 0.644
    vmax = "{:.2f}".format(vmax)
    await ctx.send(f"Output in AH77: {vmax} Kts")

@bot.command(name='crw')
async def crw(ctx, day:int, month:int, year:int):
    import requests
    
    #For cases where single digit numbers exist for month and day:
    month_f = str(month).zfill(2)
    day_f = str(day).zfill(2)

    #Opening the URL:
    url = f"https://coralreefwatch.noaa.gov/data/5km/v3.1/image/daily/ssta/gif/{year}/coraltemp5km_ssta_{year}{month_f}{day_f}_large.gif?182939392919"
    response = requests.get(url)

    if response.status_code == 200:
        await ctx.send(url)
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='ohc')
async def ohc(ctx, basin:str):
    import requests
    from datetime import datetime
    from io import BytesIO
    basin = basin.upper()
    if basin not in ['NATL', 'NPAC', 'SPAC']:
        await ctx.send("This given basin name is not applicable! Valid identifiers are [NATL, NPAC, SPAC]")
        return
    
    current_datetime = datetime.now()
    year = str(current_datetime.year)
    month = str(current_datetime.month).zfill(2)
    day = str(current_datetime.day).zfill(2)

    url = f"https://www.ospo.noaa.gov/Visualization01/cData/Blended/OHC/{basin}/OHC-PNG/OHC-PNG_{basin}_{year}{month}{day}.png"
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='iso26')
async def iso26(ctx, basin:str):
    import requests
    from datetime import datetime
    from io import BytesIO
    basin = basin.upper()
    if basin not in ['NATL', 'NPAC', 'SPAC']:
        await ctx.send("This given basin name is not applicable! Valid identifiers are [NATL, NPAC, SPAC]")
        return
    
    current_datetime = datetime.now()
    year = str(current_datetime.year)
    month = str(current_datetime.month).zfill(2)
    day = str(current_datetime.day).zfill(2)

    url = f"https://www.ospo.noaa.gov/Visualization01/cData/Blended/OHC/{basin}/H26-PNG/H26-PNG_{basin}_{year}{month}{day}.png"
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='mpi')
async def mpi(ctx, basin:str):
    import requests
    from io import BytesIO

    basin = basin.upper()
    if basin not in ['ATL', 'NIND', 'SIND', 'EPAC', 'WPAC', 'SPAC']:
        await ctx.send("This given basin name is not applicable! Valid identifiers are [ATL, EPAC, WPAC, NIND, SIND, SPAC]")
        return
    basin = basin.lower()

    url = f"http://wxmaps.org/pix/{basin}pot.png"

    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")


@bot.command(name='tcsst')
async def tcsst(ctx, btkID: str):
    import discord
    import urllib3
    from bs4 import BeautifulSoup
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    from matplotlib.lines import Line2D
    import numpy as np
    import netCDF4
    import io
    import os
    from datetime import datetime, timedelta

    btkID = btkID.lower()
    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    async def generate_and_send_image(btkID, DateTime, centerX, centerY, stormName):
        # Generate the SST map image
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        ax.coastlines()
        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels = False   # suppress top labels
        gls.right_labels = False  # suppress right labels

        # Plot SST data from 10 degC to 35 degC
        c = ax.contourf(lon, lat, sst, levels=np.arange(10, 35, 1), transform=ccrs.PlateCarree(), cmap='jet', extend='both')
        # Add small contour lines for all SSTs
        contour = ax.contour(lon, lat, sst, levels=np.arange(10, 35, 1), colors='black', linewidths=0.5, transform=ccrs.PlateCarree())
        # Add a contour line for 26 degrees Celsius
        contour_level = 26
        contour = ax.contour(lon, lat, sst, levels=[contour_level], colors='black', linewidths=2, transform=ccrs.PlateCarree())

        plt.colorbar(c, label='Sea Surface Temperature (°C)')

        legend_elements = [
            Line2D([0], [0], marker='x', color='k', label=f'Storm location as of {DateTime[-1]}', markerfacecolor='#444764', markersize=10),
            Line2D([0], [0], marker='_', color='k', label='26 degC SST Isotherm', markerfacecolor='#444764', markersize=10),
        ]

        plt.scatter(centerX, centerY, color='k', marker='x', zorder=10000000)
        ax.set_extent([centerX - 10, centerX + 10, centerY - 10, centerY + 10], crs=ccrs.PlateCarree())
        plt.title(f'SST Map over {btkID.upper()} {stormName}:')
        ax.legend(handles=legend_elements, loc='upper center')
        plt.tight_layout()
        image_path = f'{btkID}_SST_Map.png'
        plt.savefig(image_path, format='png')
        plt.close()

        # Send the generated image
        await send_image(image_path)

        # Remove the temporary image file
        os.remove(image_path)

    if btkID[:2] in ['sh', 'wp', 'io']:
        btkUrl = f'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/JTWC/b{btkID}2024.dat'
    else:
        btkUrl = f'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/NHC/b{btkID}2024.dat'

    btk_data = fetch_url(btkUrl)
    parsed_data = parse_data(btk_data)
    lines = parsed_data.split('\n')
    cdx, cdy, DateTime, timeCheck = [], [], [], []
    stormName = ""

    for line in lines:
        if line.strip():
            parameters = line.split(',')
            if parameters[6][-1] == 'S':
                cdy.append((float(parameters[6][:-1].strip()) / 10) * -1)
            else:
                cdy.append(float(parameters[6][:-1].strip()) / 10)
            if parameters[7][-1] == 'W':
                cdx.append((float(parameters[7][:-1].strip()) / 10) * -1)
            else:
                cdx.append(float(parameters[7][:-1].strip()) / 10)
            timeCheck.append((parameters[2][-2:].strip()))
            date = parameters[2].strip()
            date = f'{date[:4]}-{date[4:6]}-{date[6:8]} {timeCheck[-1]}:00:00'
            DateTime.append(date)
            stormName = parameters[27].strip()

    centerX, centerY = cdx[-1], cdy[-1]

    # Get the current date
    current_date = datetime.now()

    # Subtract two days from the current date
    two_days_ago = current_date - timedelta(days=2)

    # Extract year, month, and day components from the two days ago date
    year = str(two_days_ago.year)
    month = str(two_days_ago.month).zfill(2)  # Zero-padding for single digit months
    day = str(two_days_ago.day).zfill(2)  # Zero-padding for single digit days

    # Construct the modified URL using the extracted components
    url = f"https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{year}{month}/oisst-avhrr-v02r01.{year}{month}{day}_preliminary.nc"

    # Download the netCDF file
    response = http.request('GET', url)
    with open('sst_data.nc', 'wb') as file:
        file.write(response.data)

    # Open the downloaded netCDF file
    dataset = netCDF4.Dataset('sst_data.nc')

    # Extract latitude, longitude, and SST data
    lat = dataset.variables['lat'][:]
    lon = dataset.variables['lon'][:]
    sst = dataset.variables['sst'][0, 0, :, :]  # Assuming time and zlev dimensions are 1
    
    # Generate and send the SST map image
    await generate_and_send_image(btkID, DateTime, centerX, centerY, stormName)
    dataset.close()
    # Clean up: remove the downloaded netCDF file
    os.remove('sst_data.nc')


@bot.command(name='tcsst_custom')
async def tcsst_custom(ctx, centerY:float, centerX:float, offset=0):
    import discord
    import urllib3
    from bs4 import BeautifulSoup
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    from matplotlib.lines import Line2D
    import numpy as np
    import netCDF4
    import io
    import os
    from datetime import datetime, timedelta

    if centerY < -90 or centerY > 90 or centerX > 179.99 or centerX < -179.99:
        await ctx.send("Out of bounds!")
        return

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    async def generate_and_send_image(centerX, centerY):
        # Generate the SST map image
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        ax.coastlines()
        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels = False   # suppress top labels
        gls.right_labels = False  # suppress right labels

        # Plot SST data from 10 degC to 35 degC
        c = ax.contourf(lon, lat, sst, levels=np.arange(10, 35, 1), transform=ccrs.PlateCarree(), cmap='jet', extend='both')
        # Add small contour lines for all SSTs
        contour = ax.contour(lon, lat, sst, levels=np.arange(10, 35, 1), colors='black', linewidths=0.5, transform=ccrs.PlateCarree())
        # Add a contour line for 26 degrees Celsius
        contour_level = 26
        contour = ax.contour(lon, lat, sst, levels=[contour_level], colors='black', linewidths=2, transform=ccrs.PlateCarree())

        plt.colorbar(c, label='Sea Surface Temperature (°C)')

        legend_elements = [
            Line2D([0], [0], marker='x', color='k', label=f'Storm location', markerfacecolor='#444764', markersize=10),
            Line2D([0], [0], marker='_', color='k', label='26 degC SST Isotherm', markerfacecolor='#444764', markersize=10),
        ]

        plt.scatter(centerX, centerY, color='k', marker='x', zorder=10000000)
        if offset == 0:
            ax.set_extent([centerX - 10, centerX + 10, centerY - 10, centerY + 10], crs=ccrs.PlateCarree())
        else:
            ax.set_extent([centerX - offset, centerX + offset, centerY - offset, centerY + offset], crs=ccrs.PlateCarree())
        plt.title(f'SST Map over ({centerY}, {centerX}):')
        ax.legend(handles=legend_elements, loc='upper center')
        plt.tight_layout()
        image_path = f'SST_Map.png'
        plt.savefig(image_path, format='png')
        plt.close()

        # Send the generated image
        await send_image(image_path)

        # Remove the temporary image file
        os.remove(image_path)


    # Get the current date
    current_date = datetime.now()

    # Subtract two days from the current date
    two_days_ago = current_date - timedelta(days=2)

    # Extract year, month, and day components from the two days ago date
    year = str(two_days_ago.year)
    month = str(two_days_ago.month).zfill(2)  # Zero-padding for single digit months
    day = str(two_days_ago.day).zfill(2)  # Zero-padding for single digit days

    # Construct the modified URL using the extracted components
    url = f"https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{year}{month}/oisst-avhrr-v02r01.{year}{month}{day}_preliminary.nc"

    # Download the netCDF file
    response = http.request('GET', url)
    with open('sst_data.nc', 'wb') as file:
        file.write(response.data)

    # Open the downloaded netCDF file
    dataset = netCDF4.Dataset('sst_data.nc')

    # Extract latitude, longitude, and SST data
    lat = dataset.variables['lat'][:]
    lon = dataset.variables['lon'][:]
    sst = dataset.variables['sst'][0, 0, :, :]  # Assuming time and zlev dimensions are 1

    # Generate and send the SST map image
    await generate_and_send_image(centerX, centerY)
    dataset.close()
    # Clean up: remove the downloaded netCDF file
    os.remove('sst_data.nc')

@bot.command(name='ersst')
async def ersst(ctx, month:int, year:int):
    import requests
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    from netCDF4 import Dataset
    import os
    from matplotlib.colors import ListedColormap
    from PIL import Image

    await ctx.send("Please wait as the data loads.")
    
    def image_to_hex_array(image_path, x_range, y_coord, exclude_colors):
        # Open the image
        img = Image.open(image_path)
        
        # Convert the image to a NumPy array
        img_array = np.array(img)

        # Check if the array has an alpha channel
        if img_array.shape[2] == 4:
            # If alpha channel is present, remove it
            img_array = img_array[:, :, :3]

        # Extract colors from the specified coordinates
        colors = []
        for x in range(x_range[0], x_range[1] + 1):
            color = img_array[y_coord, x, :3]
            hex_color = '#%02x%02x%02x' % (color[0], color[1], color[2])

            # Exclude specified colors
            if hex_color not in exclude_colors:
                colors.append(hex_color)
        width, height = img.size
        print(width, height)
        return colors

    # Specify extraction parameters
    x_range = (52, 1084)
    y_coord = 28
    exclude_colors = ['#0b0004', '#280024', '#130016', '#4d418d', '#00000c', '#001377',
                    '#000412', '#00264f', '#004267', '#8e8e8e', '#2a2a2a', '#c4c4c4',
                    '#6d5a00', '#3f3300', '#1e1300', '#824000', '#1c0900', '#a92300',
                    '#970000', '#220400', '#881d00', '#420000', '#0b0000', '#8E8E8E',
                    '#262626', '#2A2A2A', '#747474', '#C4C4C4', '#6D5A00', '#E0B900',
                    '#6D5A00', '#181400', '#3F3300', '#B69400', '#E5BA00', '#AD6C00', 
                    '#1E1300', '#040200', '#824000', '#DB6C00', '#DA4A00', '#612100',
                    '#1C0900', '#4B1000', '#A92300', '#F23300', '#0086CF', '#004267', 
                    '#000A15', '#00264F', '#0060C7', '#0075F3', '#002BB7', '#000412',
                    '#000315', '#001377', '#001FC0']

    # Extract colors
    extracted_colors = image_to_hex_array('crw.png', x_range, y_coord, exclude_colors)

    # Create the colormap
    crw = ListedColormap(extracted_colors, name='crw')

    if year < 1854 or year > 2024:
        await ctx.send("The data for this year does not exist.")
        return
    
    month_f = str(month).zfill(2)
    
    url = f"https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/netcdf/ersst.v5.{year}{month_f}.nc"
    destination = f'ersst.v5.{year}{month_f}.nc'

    response = requests.get(url)
    with open(destination, 'wb') as file:
        file.write(response.content)
    #offset_value =  -0.009103 * year + 18.19 old algorithm if the new one goes wrong
    
    if year < 1901:
        offset_value = -0.006971 * year + 14.11
    elif year < 1991:
        offset_value = -0.007914 * year + 15.87
    else:
        offset_value = 0

    file_path = destination
    # Read the original NetCDF file
    with Dataset(file_path, 'r') as nc:
        lon = nc.variables['lon'][:]
        lat = nc.variables['lat'][:]
        ssta = nc.variables['ssta'][0, 0, :, :]

        # Modify the variable (e.g., add an offset)
        ssta_modified = ssta + offset_value  # Adjust the offset as needed

    fig = plt.figure(figsize=(10, 6), dpi=200)


    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')

    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='black')
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='black')

    lon_shifted = np.where(lon < 180, lon - 360, lon)

    # Plot the SST Anomaly data
    pcm = ax.pcolormesh(lon, lat, ssta_modified, transform=ccrs.PlateCarree(), cmap=crw, vmin=-5.1, vmax=5.1)
    
    # Add colorbar
    cbar = plt.colorbar(pcm, ax=ax, orientation='vertical', fraction=0.02)
    cbar.set_label('Sea Surface Temperature Anomaly (°C)')
    Month = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    plt.title(f'ERSSTv5 graph for {Month[month]} {year}', loc='left')
    range_label = f'Climatology Range: {year-30} to {year-1}'
    plt.title(range_label, loc='right')
    plt.tight_layout()
    image_path = f'{month}_{year}_ERSST_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)


    os.remove(file_path)
    os.remove(image_path)

@bot.command(name='tcdat')
async def tcdat(ctx, btkID:str, yr:str):
    import csv

    def number_to_word_category(number):
        if not (0 <= number <= 35):
            return "Number out of range (0-35)"
        categories = {
            0: "ZERO",
            1: "ONE",
            2: "TWO",
            3: "THREE",
            4: "FOUR",
            5: "FIVE",
            6: "SIX",
            7: "SEVEN",
            8: "EIGHT",
            9: "NINE",
            10: "TEN",
            11: "ELEVEN",
            12: "TWELVE",
            13: "THIRTEEN",
            14: "FOURTEEN",
            15: "FIFTEEN",
            16: "SIXTEEN",
            17: "SEVENTEEN",
            18: "EIGHTEEN",
            19: "NINETEEN",
            20: "TWENTY",
            21: "TWENTYONE",
            22: "TWENTYTWO",
            23: "TWENTYTHREE",
            24: "TWENTYFOUR",
            25: "TWENTYFIVE",
            26: "TWENTYSIX",
            27: "TWENTYSEVEN",
            28: "TWENTYEIGHT",
            29: "TWENTYNINE",
            30: "THIRTY",
            31: "THIRTYONE",
            32: "THIRTYTWO",
            33: "THIRTYTHREE",
            34: "THIRTYFOUR",
            35: "THIRTYFIVE"
        }

        return categories[number]

    print(f"Command received from server: {ctx.guild.name}")
    btkID = btkID.upper()
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'CARMEN 1974']
    check = f"{btkID} {yr}"
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    if(btkID == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    
    IBTRACS_ID = f"{btkID}{yr}"
    basin = ""
    atcf_id = ""
    year = ""
    name = ""
    flag = False
    atcfID = []
    with open('ibtracs.ALL.list.v04r00.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]):
                    atcfID.append(lines[18])
                    basin = lines[3]
                    name = lines[5]
    # ['NA', 'EP','WP', NI, SI, SP]
    print(atcfID)
    for i in range(len(atcfID)):
        if len(atcfID[i]) > 1:
            atcf_id = atcfID[i]
            break
    year = atcf_id[-4:]
    ba = atcf_id[:2]
    basin_map_XX = {"AL":"ATL", "EP":"EPAC", "CP":"CPAC", "WP":"WPAC", "IO":"IO", "SH":"SHEM"}
    basin_map_20XX = {"AL":"AL", "EP":"EP", "CP":"CP", "WP":"WP", "IO":"IO", "AS":"IO", "BB":"IO", "SH":"SH", "SI":"SH", "SP":"SH"}
    header_20XX = {"AL":"L", "EP":"E", "CP":"C", "WP":"W", "AS":"A", "BB":"B", "SH":"S", "SI":"S", "SP":"P"}
    
    url = ""
    print(atcf_id)
    if int(yr) > 2017:
        checked_atcf_id = basin_map_20XX[ba] + atcf_id[2:]
        url += f"https://www.nrlmry.navy.mil/tcdat/tc{year}/{basin_map_20XX[ba]}/{checked_atcf_id}/"
    else:
        if name == "NOT_NAMED":
            name = f"{number_to_word_category(int(atcf_id[2:4]))}"
        ATCF_Header = atcf_id[2:4] + header_20XX[ba]
        url += f"https://www.nrlmry.navy.mil/tcdat/tc{year[-2:]}/{basin_map_XX[ba]}/{ATCF_Header}.{name}/"

    await ctx.send(url)

@bot.command(name='rammb')
async def rammb(ctx, btkID:str, yr:str):
    import csv

    print(f"Command received from server: {ctx.guild.name}")
    btkID = btkID.upper()
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'VICKY 2020', 'JOYCE 2018', 'GORDON 1979', 'BENI 2003', 'MARK 1992', 'CARMEN 1974']
    check = f"{btkID} {yr}"
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    
    IBTRACS_ID = f"{btkID}{yr}"
    basin = ""
    atcf_id = ""
    year = ""
    name = ""
    flag = False
    atcfID = []
    with open('ibtracs.ALL.list.v04r00.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]):
                    atcfID.append(lines[18])
                    basin = lines[3]
                    if int(lines[6][5:7]) > 6:
                        print(lines[6][5:7])
                        flag = True
    for i in range(len(atcfID)):
        if len(atcfID[i]) > 1:
            atcf_id += atcfID[i]
            break
    print(atcf_id)
    ATCF_Header = ""
    if basin == 'SI' or basin == 'SP':
        ATCF_Header = "sh" + atcf_id[2:4] + atcf_id[4:] if flag == False else "sh" + atcf_id[2:4] + str(int(yr)+1)
    elif basin == 'NI':
        ATCF_Header = "io" + atcf_id[2:]
    else:
        ATCF_Header = atcf_id.lower()
    url = f"https://rammb-data.cira.colostate.edu/tc_realtime/storm.asp?storm_identifier={ATCF_Header}"
    await ctx.send(url)

@bot.command(name='digty')
async def digty(ctx, name:str, yr:str):
    name = name.upper()
    if(name == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    jma = ""
    with open("bst_all.txt", "r") as file:
        data = file.read()
        data = data.split('\n')
        for i in range(len(data)-1):
            row = data[i].split()
            
            if row[0] == '66666':
                
                if len(row) == 7:
                    continue
                if (row[7] == name or row[6] == name) and yr[2:] == row[1][:2]:
                    print(row)
                    print(len(row))
                    jma += yr + row[1][2:]
                    break
    print(jma)
    url = f"http://agora.ex.nii.ac.jp/digital-typhoon/summary/wnp/s/{jma}.html.en"
    await ctx.send(url)
    


@bot.command(name='ibtracs')
async def ibtracs(ctx, btkID:str, yr:str):
    import csv
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.lines import Line2D
    import os
    import numpy as np

    print(f"Command received from server: {ctx.guild.name}")
    btkID = btkID.upper()
    if btkID == 'BENTO':
        btkID = 'BENTOJANA'
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'VICKY 2020', 'JOYCE 2018', 'GORDON 1979', 'BENI 2003', 'MARK 1992', 'NADINE 1978',
                  'WINNIE 1978', 'HARVEY 2005', 'FREDA 1981', 'POLLY 1970', 'LOUISE 1970', 'LUCY 1962', 'CARMEN 1974']
    check = f"{btkID} {yr}"
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    if(btkID == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    #Load in the loops for finding the latitude and longitude...
    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, winds, status, timeCheck, DateTime = [], [], [], [], [], []
    storm_name = ""
    s_ID = ""
    idl = False
    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r00.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]):
                    DateTime.append(lines[6])
                    s_ID = lines[18]
                    cdx.append(lines[20])
                    if(cdx[-1] == ' '):
                        pass
                    elif(float(cdx[-1]) < -178 or float(cdx[-1]) > 178):
                        idl = True
                    cdy.append(lines[19])
                    winds.append(lines[23])
                    status.append(lines[22])
                    timeCheck.append(lines[6][-8:-6])
                    storm_name = lines[5]
    await ctx.send("System located in database, generating track...")
    #-------------------------------DEBUG INFORMATION-----------------------------------
    print(cdx, "\n", cdy, "\n", winds, "\n", status, "\n", timeCheck, "\n", storm_name)
    #-----------------------------------------------------------------------------------
    
    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

    ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    maxLat, minLat, maxLong, minLong = -999, 999, -999, 999
    vmax, statMaxIndx = 0, 0

    #Plotting the markers...
    for i in range(0, len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ' or winds[i] == ' ':
            continue
        
        if idl == True:
            coord_x, coord_y = float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180, float(cdy[i])
        else:
            coord_x, coord_y = float(cdx[i]), float(cdy[i])
        wind = int(winds[i])

        #Setup for finding bounding box...
        if(maxLat < coord_y):
            maxLat = coord_y
        if(minLat > coord_y):
            minLat = coord_y
        if(maxLong < coord_x):
            maxLong = coord_x
        if(minLong > coord_x):
            minLong = coord_x 
        
        #Setup for displaying VMAX as well as peak Status...
        if vmax < wind:
            vmax = wind
            statMaxIndx = i

        if(int(timeCheck[i]) % 6  == 0):
            #Mark scatter plots...
            if status[i] in ['DB', 'WV', 'LO', 'MD']:
                plt.scatter(coord_x, coord_y, color='#444764', marker='^', zorder=3)
            elif status[i] == 'EX':
                if int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='^', zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='^', zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='^', zorder=3)
            elif status[i] == 'SS':
                plt.scatter(coord_x, coord_y, color='g', marker='s', zorder=3)
            elif status[i] == 'SD':
                plt.scatter(coord_x, coord_y, color='b', marker='s', zorder=3)
            else:
                if int(wind) >= 137:
                    plt.scatter(coord_x, coord_y, color='m', marker='o', zorder=3)
                elif int(wind) >= 112:
                    plt.scatter(coord_x, coord_y, color='r', marker='o', zorder=3)
                elif int(wind) >= 96:
                    plt.scatter(coord_x, coord_y, color='#ff5908', marker='o', zorder=3)
                elif int(wind) >= 81:
                    plt.scatter(coord_x, coord_y, color='#ffa001', marker='o', zorder=3)
                elif int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='o', zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='o', zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='o', zorder=3)

    #Setting the coordinates for the bounding box...
    center_x = (minLong + maxLong)/2
    center_y = (minLat + maxLat)/2

    center_width = abs(maxLong - minLong)
    center_height = abs(maxLat - minLat)

    ratio = (center_height/center_width)
    print(ratio)
    if ratio < 0.3:
        ax.set_xlim(center_x-center_width, center_x+center_width)
        ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
    elif ratio > 0.7:
        ax.set_xlim(center_x-(center_height), center_x+(center_height))
        ax.set_ylim(center_y-center_height, center_y+center_height)
    else:
        ax.set_xlim(center_x-center_width, center_x+center_width)
        ax.set_ylim(center_y-center_height, center_y+center_height)

    #Defining the legend box for the plot...
    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='Non-Tropical',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='Sub-Tropical',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Tropical Depression',markerfacecolor='b', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Tropical Storm',markerfacecolor='g', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 1',markerfacecolor='#ffff00', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 2',markerfacecolor='#ffa001', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 3',markerfacecolor='#ff5908', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 4',markerfacecolor='r', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 5',markerfacecolor='m', markersize=10),
    ]

    #Building the function that calculates ACE...
    def calc_ACE(winds, timeCheck):
        ace = 0
    
        for i in range(len(winds)):
            if(winds[i] == ' '):
                continue
            time = int(timeCheck[i]) % 6
            if(time==0 and int(winds[i]) >= 34 and status[i] not in ['DB', 'LO', 'WV', 'EX']): #If it is synoptic time and meets...
                ace += (int(winds[i]) ** 2) / 10000
        return "{:.4f}".format(ace)

    #Plotting the TC Path...
    LineX = []
    LineY = []

    for i in range(len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ':
            continue
        if idl == True:
            LineX.append(float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180)
        else:
            LineX.append(float(cdx[i]))
        LineY.append(float(cdy[i]))

    plt.plot(LineX, LineY, color="k", linestyle="-")
    plt.text(LineX[0], LineY[0]+0.5, f'{DateTime[0]}')
    plt.text(LineX[len(LineX)-1], LineY[len(LineX)-1]+0.5, f'{DateTime[len(LineX)-1]}')

    #Applying final touches...
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    if s_ID == ' ':
        plt.title(f'{storm_name} {yr}')
    else:
        plt.title(f'{s_ID} {storm_name}')
    plt.title(f'VMAX: {vmax} Kts', loc='left', fontsize=9)
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right', fontsize=9)
    ax.legend(handles=legend_elements, loc='upper right' if btkID[:2]=="SH" or btkID[:2]=="EP" else "upper left")
    plt.grid(True)
    plt.tight_layout()
    
    r = np.random.randint(1, 10)
    image_path = f'Track_Map{r}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)  

@bot.command(name='otd')
async def otd(ctx, day:int, month:int):
    import csv
    import os

    ID = ""
    Name = ""
    resultOTD = []
    await ctx.send("Hold as the file is generated.")
    with open('ibtracs.ALL.list.v04r00.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                if int(lines[6][5:7]) == month and int(lines[6][8:10]) == day:
                    if lines[18] == "":
                        continue
                    ID = lines[18]
                    Name = lines[5]
                    res = f"{ID} {Name}"
                    if res not in resultOTD:
                        resultOTD.append(res)

    # Write the results to a text file
    output_file_path = "otd_results.txt"
    with open(output_file_path, "w") as output_file:
        for entry in resultOTD:
            output_file.write(entry + "\n")

    # Send the text file as an attachment
    with open(output_file_path, "rb") as output_file:
        await ctx.send(file=discord.File(output_file))

    # Delete the temporary text file
    os.remove(output_file_path)

@bot.command(name='storm_name')
async def storm_name(ctx, name:str):
    import csv
    import os
    name = name.upper()
    ID = ""

    resultYr = []
    await ctx.send("Hold as the database is accessed.")
    with open('ibtracs.ALL.list.v04r00.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                if lines[5] == name:
                    if lines[18] == "":
                        continue
                    ID = lines[6][:4]

                    res = f"{ID}"
                    if res not in resultYr:
                        resultYr.append(res)
    
    res = f"Years that saw the storm name {name}: \n"
    for entry in resultYr:
        res += entry + " "
    await ctx.send(res)

@bot.command(name='season')
async def season(ctx, basin:str, yr:str):
    import csv
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.lines import Line2D
    import os
    import numpy as np
    basin = basin.upper()
    if basin not in ['NA', 'EP','WP', 'NI', 'SI', 'SP']:
        await ctx.send("The basin is not valid! Valid basins are ['NA', 'EP','WP', NI, SI, SP]")
        return
    await ctx.send("Please be patient. As this is a season, the plot may take a little while to generate.")
    idl = False
    id, cdx, cdy, winds, status, timeCheck, DateTime = [], [], [], [], [], [], []
    storm_name = []
    s_ID = ""
    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r00.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[3] == basin and yr == lines[18][-4:]:
                    DateTime.append(lines[6])
                    s_ID = lines[18]
                    id.append(s_ID)
                    cdx.append(lines[20])
                    if(cdx[-1] == ' '):
                        pass
                    elif(float(cdx[-1]) < -178 or float(cdx[-1]) > 178):
                        idl = True
                    cdy.append(lines[19])
                    winds.append(lines[23])
                    status.append(lines[22])
                    timeCheck.append(lines[6][-8:-6])
                    storm_name.append(lines[5])
        
    #-------------------------------DEBUG INFORMATION-----------------------------------
    print(cdx, "\n", cdy, "\n", winds, "\n", status, "\n", timeCheck, "\n", storm_name, "\n", id)
    #-----------------------------------------------------------------------------------
    await ctx.send("Season located in database, generating track...")
    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

    ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    maxLat, minLat, maxLong, minLong = -999, 999, -999, 999

    #Plotting the TC Path...
    LineX = []
    LineY = []
    Vmax = []
    checkID = id[0]
    for i in range(len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ':
            continue
        if checkID != id[i]:
            LineX = []
            LineY = []
            checkID = id[i]
        if idl == True:
            LineX.append(float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180)
        else:
            LineX.append(float(cdx[i]))
        LineY.append(float(cdy[i]))
        plt.plot(LineX, LineY, color="k", linestyle="-", lw=1)
    
    #Plotting the markers...
    for i in range(0, len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ' or winds[i] == ' ':
            continue

        if idl == True:
            coord_x, coord_y = float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180, float(cdy[i])
        else:
            coord_x, coord_y = float(cdx[i]), float(cdy[i])
        wind = int(winds[i])

        #Setup for finding bounding box...
        if(maxLat < coord_y):
            maxLat = coord_y
        if(minLat > coord_y):
            minLat = coord_y
        if(maxLong < coord_x):
            maxLong = coord_x
        if(minLong > coord_x):
            minLong = coord_x 

        if(int(timeCheck[i]) % 6  == 0):
            #Mark scatter plots...
            if status[i] in ['DB', 'WV', 'LO', 'MD']:
                plt.scatter(coord_x, coord_y, color='#444764', marker='^', s=15, zorder=3)
            elif status[i] == 'EX':
                if int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='^', s=15, zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='^', s=15, zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='^', s=15, zorder=3)
            elif status[i] == 'SS':
                plt.scatter(coord_x, coord_y, color='g', marker='s', s=15, zorder=3)
            elif status[i] == 'SD':
                plt.scatter(coord_x, coord_y, color='b', marker='s', s=15, zorder=3)
            else:
                if int(wind) >= 137:
                    plt.scatter(coord_x, coord_y, color='m', marker='o', s=15, zorder=3)
                elif int(wind) >= 112:
                    plt.scatter(coord_x, coord_y, color='r', marker='o', s=15, zorder=3)
                elif int(wind) >= 96:
                    plt.scatter(coord_x, coord_y, color='#ff5908', marker='o', s=15, zorder=3)
                elif int(wind) >= 81:
                    plt.scatter(coord_x, coord_y, color='#ffa001', marker='o', s=15, zorder=3)
                elif int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='o', s=15, zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='o', s=15, zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='o', s=15, zorder=3)

    if basin == 'NA':
        ax.set_extent([-110, 0, 0, 65], crs=ccrs.PlateCarree())
    elif basin == 'EP' or basin == 'CP':
        ax.set_extent([-179.99, -85, 0, 65], crs=ccrs.PlateCarree())
    elif basin == 'WP':
        ax.set_extent([95, 179.99, 0, 60], crs=ccrs.PlateCarree())
    elif basin == 'NI':
        ax.set_extent([40, 110, 0, 40], crs=ccrs.PlateCarree())
    elif basin == 'SI':
        ax.set_extent([20, 140, -40, 0], crs=ccrs.PlateCarree())
    elif basin == 'SP': 
        #Setting the coordinates for the bounding box...
        center_x = (minLong + maxLong)/2
        center_y = (minLat + maxLat)/2

        center_width = abs(maxLong - minLong)
        center_height = abs(maxLat - minLat)

        ratio = (center_height/center_width)
        print(ratio)
        if ratio < 0.3:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
        elif ratio > 0.7:
            ax.set_xlim(center_x-(center_height), center_x+(center_height))
            ax.set_ylim(center_y-center_height, center_y+center_height)
        else:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-center_height, center_y+center_height)
       

    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='EX/LO/DB',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='SS/SD',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='TD',markerfacecolor='b', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='TS',markerfacecolor='g', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C1',markerfacecolor='#ffff00', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C2',markerfacecolor='#ffa001', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C3',markerfacecolor='#ff5908', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C4',markerfacecolor='r', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C5',markerfacecolor='m', markersize=10),
    ]

    #Building the function that calculates ACE...
    def calc_ACE(winds, timeCheck):
        ace = 0
    
        for i in range(len(winds)):
            if(winds[i] == ' '):
                continue
            time = int(timeCheck[i]) % 6
            if(time==0 and int(winds[i]) >= 34 and status[i] not in ['DB', 'LO', 'WV', 'EX']): #If it is synoptic time and meets...
                ace += (int(winds[i]) ** 2) / 10000
        return "{:.4f}".format(ace)
    

    #Applying final touches...
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Season Summary: {yr} {basin}', loc='left')
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right', fontsize=9)
    location = ""
    if(basin == 'EP'):
        location = "upper right"
    elif(basin == 'SP' or basin == 'SI'):
        location = "upper left"
    else:
        location = "upper left"
    ax.legend(handles=legend_elements, loc=location)
    plt.grid(True)
    plt.tight_layout()
    
    r = np.random.randint(1, 10)
    image_path = f'Track_Map{r}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)

@bot.command(name='seasongen_atcf')
async def seasongen_atcf(ctx, url:str, basin=''):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.lines import Line2D
    import urllib3
    from bs4 import BeautifulSoup
    import os
    import numpy as np
    basin = basin.upper()
    
    idl = False
    id, cdx, cdy, winds, status, timeCheck, DateTime = [], [], [], [], [], [], []
    storm_name = []
    s_ID = ""
    

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()


    btk_data = fetch_url(url)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')
    idl = False
    cdx, cdy, winds, status, timeCheck, pres, DateTime, r34 = [], [], [], [], [], [], [], []
    stormName = ""

    for line in lines:
        if line.strip():
            stormData = line.split(',')

            #Checking Longitudinal Hemisphere...
            if(stormData[7][-1] == 'W'):
                cdx.append((float(stormData[7][:-1].strip())/10)*-1)
            else:
                cdx.append(float(stormData[7][:-1].strip())/10)
            if(cdx[-1] == ' '):
                pass
            elif(float(cdx[-1]) < -175 or float(cdx[-1]) > 175):
                idl = True
            #Checking Latitudinal Hemisphere...
            if(stormData[6][-1] == 'S'):
                cdy.append((float(stormData[6][:-1].strip())/10)*-1)
            else:
                cdy.append(float(stormData[6][:-1].strip())/10)
            id.append(stormData[1].strip())
            status.append(stormData[10].strip())
            winds.append(int(stormData[8].strip()))
            presVal = stormData[9].strip()
            pres.append(int(presVal) if presVal != '' else 1010)
            stormData[2] = stormData[2].strip() #Bugfix
            timeCheck.append(int(stormData[2][-2:]))
        
    #-------------------------------DEBUG INFORMATION-----------------------------------
    print(cdx, "\n", cdy, "\n", winds, "\n", status, "\n", timeCheck, "\n", storm_name, "\n", id)
    #-----------------------------------------------------------------------------------
    await ctx.send("Season located in database, generating track...")
    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

    ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    maxLat, minLat, maxLong, minLong = -999, 999, -999, 999

    #Plotting the TC Path...
    LineX = []
    LineY = []
 
    checkID = id[0]
    for i in range(len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ':
            continue
        if checkID != id[i]:
            LineX = []
            LineY = []
            checkID = id[i]
        if idl == True:
            LineX.append(float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180)
        else:
            LineX.append(float(cdx[i]))
        LineY.append(float(cdy[i]))
        plt.plot(LineX, LineY, color="k", linestyle="-", lw=1)
    
    #Plotting the markers...
    for i in range(0, len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ' or winds[i] == ' ':
            continue

        if idl == True:
            coord_x, coord_y = float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180, float(cdy[i])
        else:
            coord_x, coord_y = float(cdx[i]), float(cdy[i])
        wind = int(winds[i])

        #Setup for finding bounding box...
        if(maxLat < coord_y):
            maxLat = coord_y
        if(minLat > coord_y):
            minLat = coord_y
        if(maxLong < coord_x):
            maxLong = coord_x
        if(minLong > coord_x):
            minLong = coord_x 

        if(int(timeCheck[i]) % 6  == 0):
            #Mark scatter plots...
            if status[i] in ['DB', 'WV', 'LO', 'MD']:
                plt.scatter(coord_x, coord_y, color='#444764', marker='^', s=15, zorder=3)
            elif status[i] == 'EX':
                if int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='^', s=15, zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='^', s=15, zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='^', s=15, zorder=3)
            elif status[i] == 'SS':
                plt.scatter(coord_x, coord_y, color='g', marker='s', s=15, zorder=3)
            elif status[i] == 'SD':
                plt.scatter(coord_x, coord_y, color='b', marker='s', s=15, zorder=3)
            else:
                if int(wind) >= 137:
                    plt.scatter(coord_x, coord_y, color='m', marker='o', s=15, zorder=3)
                elif int(wind) >= 112:
                    plt.scatter(coord_x, coord_y, color='r', marker='o', s=15, zorder=3)
                elif int(wind) >= 96:
                    plt.scatter(coord_x, coord_y, color='#ff5908', marker='o', s=15, zorder=3)
                elif int(wind) >= 81:
                    plt.scatter(coord_x, coord_y, color='#ffa001', marker='o', s=15, zorder=3)
                elif int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='o', s=15, zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='o', s=15, zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='o', s=15, zorder=3)

    if basin == 'NA':
        ax.set_extent([-110, 0, 0, 65], crs=ccrs.PlateCarree())
    elif basin == 'EP' or basin == 'CP':
        ax.set_extent([-179.99, -85, 0, 65], crs=ccrs.PlateCarree())
    elif basin == 'WP':
        ax.set_extent([95, 179.99, 0, 60], crs=ccrs.PlateCarree())
    elif basin == 'NI':
        ax.set_extent([40, 110, 0, 40], crs=ccrs.PlateCarree())
    elif basin == 'SI':
        ax.set_extent([20, 140, -40, 0], crs=ccrs.PlateCarree())
    elif basin == 'SP' or basin == '': 
        #Setting the coordinates for the bounding box...
        center_x = (minLong + maxLong)/2
        center_y = (minLat + maxLat)/2

        center_width = abs(maxLong - minLong)
        center_height = abs(maxLat - minLat)

        ratio = (center_height/center_width)
        print(ratio)
        if ratio < 0.3:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
        elif ratio > 0.7:
            ax.set_xlim(center_x-(center_height), center_x+(center_height))
            ax.set_ylim(center_y-center_height, center_y+center_height)
        else:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-center_height, center_y+center_height)
       

    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='EX/LO/DB',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='SS/SD',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='TD',markerfacecolor='b', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='TS',markerfacecolor='g', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C1',markerfacecolor='#ffff00', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C2',markerfacecolor='#ffa001', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C3',markerfacecolor='#ff5908', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C4',markerfacecolor='r', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C5',markerfacecolor='m', markersize=10),
    ]

    #Building the function that calculates ACE...
    def calc_ACE(winds, timeCheck):
        ace = 0
    
        for i in range(len(winds)):
            if(winds[i] == ' '):
                continue
            time = int(timeCheck[i]) % 6
            if(time==0 and int(winds[i]) >= 34 and status[i] not in ['DB', 'LO', 'WV', 'EX']): #If it is synoptic time and meets...
                ace += (int(winds[i]) ** 2) / 10000
        return "{:.4f}".format(ace)
    

    #Applying final touches...
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Season Summary: ', loc='left')
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right', fontsize=9)
    location = ""
    if(basin == 'EP'):
        location = "upper right"
    elif(basin == 'SP' or basin == 'SI'):
        location = "upper left"
    else:
        location = "upper left"
    ax.legend(handles=legend_elements, loc=location)
    plt.grid(True)
    plt.tight_layout()
    
    r = np.random.randint(1, 10)
    image_path = f'Track_Map{r}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)

@bot.command(name='seasongen_hurdat')
async def seasongen_hurdat(ctx, url:str, basin=''):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.lines import Line2D
    import urllib3
    from bs4 import BeautifulSoup
    import numpy as np
    import os

    await ctx.send("Please be patient. As this is a season, the plot may take a little while to generate.")
    basin = basin.upper()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()


    btk_data = fetch_url(url)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')

    idl = False
    id, cdx, cdy, winds, status, timeCheck, DateTime, pres = [], [], [], [], [], [], [], []
    storm_name = []
    s_ID = ""

    #Plotting the TC Path...
    LineX = []
    LineY = []
    Vmax = []
    extLines = []


    for line in lines:
        if line.strip():
            stormData = line.split(',')
            if len(stormData) == 4:
                extLines.append(stormData)
                continue
            else:
                #Checking Longitudinal Hemisphere...
                if(stormData[5][-1] == 'W'):
                    cdx.append(float(stormData[5][:-1].strip())*-1)
                else:
                    cdx.append(float(stormData[5][:-1].strip()))
                
                if(cdx[-1] == ' '):
                    pass
                elif(float(cdx[-1]) < -178 or float(cdx[-1]) > 178):
                    idl = True

                #Checking Latitudinal Hemisphere...
                if(stormData[4][-1] == 'S'):
                    cdy.append(float(stormData[4][:-1].strip())*-1)
                else:
                    cdy.append(float(stormData[4][:-1].strip()))
                
                status.append(stormData[3].strip())
                winds.append(int(stormData[6].strip()))
                pres.append(int(stormData[7].strip()))
                stormData[1] = stormData[1].strip() #Bugfix
                timeCheck.append(int(stormData[1][:2]))
                extLines.append(stormData)

    print(extLines)


    #-------------------------------DEBUG INFORMATION-----------------------------------
    print(cdx, "\n", cdy, "\n", winds, "\n", status, "\n", timeCheck, "\n")
    #-----------------------------------------------------------------------------------

    
    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))


    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

    ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    maxLat, minLat, maxLong, minLong = -999, 999, -999, 999

    LineX = []
    LineY = []
    index = 0
    for i in range(len(extLines)):
        if(len(extLines[i]) == 4):
            LineX = []
            LineY = []
            continue

        if cdx[index] == ' ' or cdy[index] == ' ':
            continue
        
        if idl == True:
            LineX.append(float(cdx[index])+180 if float(cdx[index])<0 else float(cdx[index])-180)
        else:
            LineX.append(float(cdx[index]))
        LineY.append(float(cdy[index]))
        plt.plot(LineX, LineY, color="k", linestyle="-", lw=1)
        index += 1


    #Plotting the markers...
    for i in range(0, len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ' or winds[i] == ' ':
            continue

        if idl == True:
            coord_x, coord_y = float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180, float(cdy[i])
        else:
            coord_x, coord_y = float(cdx[i]), float(cdy[i])
        wind = int(winds[i])

        #Setup for finding bounding box...
        if(maxLat < coord_y):
            maxLat = coord_y
        if(minLat > coord_y):
            minLat = coord_y
        if(maxLong < coord_x):
            maxLong = coord_x
        if(minLong > coord_x):
            minLong = coord_x 

        if(int(timeCheck[i]) % 6  == 0):
            #Mark scatter plots...
            if status[i] in ['DB', 'WV', 'LO', 'MD']:
                plt.scatter(coord_x, coord_y, color='#444764', marker='^', s=15, zorder=10)
            elif status[i] == 'EX':
                if int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='^', s=15, zorder=10)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='^', s=15, zorder=10)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='^', s=15, zorder=10)
            elif status[i] == 'SS':
                plt.scatter(coord_x, coord_y, color='g', marker='s', s=15, zorder=10)
            elif status[i] == 'SD':
                plt.scatter(coord_x, coord_y, color='b', marker='s', s=15, zorder=10)
            else:
                if int(wind) >= 137:
                    plt.scatter(coord_x, coord_y, color='m', marker='o', s=15, zorder=10)
                elif int(wind) >= 112:
                    plt.scatter(coord_x, coord_y, color='r', marker='o', s=15, zorder=10)
                elif int(wind) >= 96:
                    plt.scatter(coord_x, coord_y, color='#ff5908', marker='o', s=15, zorder=10)
                elif int(wind) >= 81:
                    plt.scatter(coord_x, coord_y, color='#ffa001', marker='o', s=15, zorder=10)
                elif int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='o', s=15, zorder=10)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='o', s=15, zorder=10)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='o', s=15, zorder=10)


    if basin == 'NA':
        ax.set_extent([-110, 0, 0, 65], crs=ccrs.PlateCarree())
    elif basin == 'EP' or basin == 'CP':
        ax.set_extent([-179.99, -85, 0, 65], crs=ccrs.PlateCarree())
    elif basin == 'WP':
        ax.set_extent([95, 179.99, 0, 60], crs=ccrs.PlateCarree())
    elif basin == 'NI':
        ax.set_extent([40, 110, 0, 40], crs=ccrs.PlateCarree())
    elif basin == 'SI':
        ax.set_extent([20, 140, -40, 0], crs=ccrs.PlateCarree())
    elif basin == 'SP' or basin == '': 
        #Setting the coordinates for the bounding box...
        center_x = (minLong + maxLong)/2
        center_y = (minLat + maxLat)/2

        center_width = abs(maxLong - minLong)
        center_height = abs(maxLat - minLat)

        ratio = (center_height/center_width)
        print(ratio)
        if ratio < 0.3:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
        elif ratio > 0.7:
            ax.set_xlim(center_x-(center_height), center_x+(center_height))
            ax.set_ylim(center_y-center_height, center_y+center_height)
        else:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-center_height, center_y+center_height)


    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='EX/LO/DB',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='SS/SD',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='TD',markerfacecolor='b', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='TS',markerfacecolor='g', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C1',markerfacecolor='#ffff00', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C2',markerfacecolor='#ffa001', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C3',markerfacecolor='#ff5908', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C4',markerfacecolor='r', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='C5',markerfacecolor='m', markersize=10),
    ]

    #Building the function that calculates ACE...
    def calc_ACE(winds, timeCheck):
        ace = 0

        for i in range(len(winds)):
            if(winds[i] == ' '):
                continue
            time = int(timeCheck[i]) % 6
            if(time==0 and int(winds[i]) >= 34 and status[i] not in ['DB', 'LO', 'WV', 'EX']): #If it is synoptic time and meets...
                ace += (int(winds[i]) ** 2) / 10000
        return "{:.4f}".format(ace)

    await ctx.send("Season successfully read from database, generating track...")

    #Applying final touches...
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Season Summary: ', loc='left')
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right', fontsize=9)
    location = ""
    if(basin == 'EP'):
        location = "upper right"
    elif(basin == 'SP' or basin == 'SI'):
        location = "upper left"
    else:
        location = "upper left"
    ax.legend(handles=legend_elements, loc=location)
    plt.grid(True)
    plt.tight_layout()
    r = np.random.randint(1, 10)
    image_path = f'Track_Map{r}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)

@bot.command(name='smap')
async def smap(ctx, btkID, nodeType:str):
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    from datetime import datetime
    import requests
    from matplotlib.lines import Line2D
    import os
    import urllib3
    from bs4 import BeautifulSoup
    import numpy as np

    await ctx.send("Please hold as the data is generated.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()
    btkID = btkID.lower()
    nodeType = nodeType.upper()
    if btkID[:2] in ['sh', 'wp', 'io']:
        btkUrl = f'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/JTWC/b{btkID}2024.dat'
    else:
        btkUrl = f'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/NHC/b{btkID}2024.dat'

    btk_data = fetch_url(btkUrl)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')

    cdx, cdy, winds, status, timeCheck, pres, DateTime, r34 = [], [], [], [], [], [], [], []
    stormName = ""

    for line in lines:
        if line.strip():
            parameters = line.split(',')
            if parameters[6][-1] == 'S':
                cdy.append((float(parameters[6][:-1].strip()) / 10)*-1)
            else:
                cdy.append(float(parameters[6][:-1].strip()) / 10)
        
            if parameters[7][-1] == 'W':
                cdx.append((float(parameters[7][:-1].strip()) / 10)*-1)
            else:
                cdx.append(float(parameters[7][:-1].strip()) / 10)

    print(cdx, "\n", cdy)
    current_datetime = datetime.now()
    year = str(current_datetime.year)
    month = str(current_datetime.month).zfill(2)
    day = str(current_datetime.day).zfill(2)

    # Define the storm's coordinates
    storm_lat = float(cdy[-1])  # Example latitude
    storm_lon = float(cdx[-1]) if float(cdx[-1])>0 else 360 + float(cdx[-1])  # Example longitude

    # Calculate latitude and longitude bounds for the bounding box
    lat_min = storm_lat - 10
    lat_max = storm_lat + 10
    lon_min = storm_lon - 10
    lon_max = storm_lon + 10

    url = f'https://data.remss.com/smap/wind/L3/v01.0/daily/NRT/{year}/RSS_smap_wind_daily_{year}_{month}_{day}_NRT_v01.0.nc'

    destination = f'smap{year}{month}.nc'

    response = requests.get(url)
    with open(destination, 'wb') as file:
        file.write(response.content)

    # Open the NetCDF file using xarray
    ds = xr.open_dataset(destination, decode_times=False)

    # Extract the wind variable
    wind = ds['wind']

    # Extract wind data within the bounding box
    wind_bounded = wind.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    await ctx.send("Generating data if available...")

    # Check if wind data is available within the bounding box
    if len(wind_bounded.lat) == 0 or len(wind_bounded.lon) == 0:
        await ctx.send("No data available within the bounding box.")
        ds.close()
        os.remove(destination)
    else:
        nodal = 0 if nodeType == 'ASC' else 1

        # Find the nearest latitude and longitude values in the dataset
        nearest_lat_index = np.abs(ds.lat.values - storm_lat).argmin()
        nearest_lon_index = np.abs(ds.lon.values - storm_lon).argmin()

        minute_data = ds.minute[nearest_lat_index, nearest_lon_index]
        print(minute_data)

        # Access the minute data for the nearest coordinate
        minute_data = ds.minute.isel(node=nodal).values[nearest_lat_index, nearest_lon_index]
        timePass=""

        # Check if minute data is available
        if np.isnan(minute_data):
            print("No minute data available for the nearest coordinate.")
            timePass += "NaN"
        else:
            # Print the minute data value
            print("Minute data value for the nearest coordinate:", minute_data)
            hr = str(int(minute_data) // 60).zfill(2)
            min = str(int(minute_data) % 60).zfill(2)
            timePass += f"{hr}{min} UTC"

        # Find the maximum wind value within the bounding box
        max_wind_value = wind_bounded.max()

        # Create the plot
        fig = plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())

        # Plot wind data using pcolormesh
        mesh = ax.pcolormesh(wind.lon, wind.lat, (wind.isel(node=nodal))*1.944, transform=ccrs.PlateCarree(), cmap='gist_ncar', vmin=0, vmax=150)
        contour_17 = ax.contour(wind.lon, wind.lat, wind.isel(node=nodal), levels=[17], colors='black', transform=ccrs.PlateCarree())
        contour_25 = ax.contour(wind.lon, wind.lat, wind.isel(node=nodal), levels=[25], colors='green', transform=ccrs.PlateCarree())
        contour_32 = ax.contour(wind.lon, wind.lat, wind.isel(node=nodal), levels=[32], colors='red', transform=ccrs.PlateCarree())
        
        # Add coastlines
        ax.coastlines()

        # Add gridlines
        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels=False   # suppress top labels
        gls.right_labels=False # suppress right labels

        # Set the extent of the plot to zoom into the bounding box
        ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

        # Add title
        plt.title(f'SMAP SFC Winds\nTime: {timePass}, {year}/{month}/{day}', loc='left', fontsize=7)

        # Add colorbar
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.5, extend='both')
        cbar.set_label('Wind Speed (kts)')
        # Print the maximum wind value within the bounding box
        max_wind_value = max_wind_value.values.item()*1.944  # Get the raw value

        def oneMin(raw_SMAP):
            processed_SMAP = (362.644732816453 * raw_SMAP + 2913.62505913216) / 380.88384339523

            #Display output:
            processed_SMAP = "{:.2f}".format(processed_SMAP)
            return processed_SMAP

        
        legend_elements = [
        Line2D([0], [0], marker='_', color='k', label='34kt winds', markersize=10),
        Line2D([0], [0], marker='_', color='g', label='50kt winds', markersize=10),
        Line2D([0], [0], marker='_', color='r', label='64kt winds', markersize=10),
        ]
        

        plt.title(f"Maximum 10-min wind value: {max_wind_value:.2f} kts, 1-min: {oneMin(max_wind_value)} kt", loc='right', fontsize=8)
        ax.legend(handles=legend_elements, loc='upper right')
        r = np.random.randint(1, 10)
        image_path = f'Track_Map{r}.png'
        plt.savefig(image_path, format='png', bbox_inches='tight')
        plt.close()

        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

        os.remove(image_path)
        ds.close()

        os.remove(destination)  


@bot.command(name='gridsat')
async def gridsat(ctx, cdy:float, cdx:float, hour:str, day:str, month:str, year:str):
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import numpy as np
    import requests
    import os
    await ctx.send("GRIDSAT-B1 is a large file and may take a few minutes to plot. Please be patient.")
    def download_gridsat_nc(year, month, day, hour):
        # Format year, month, day, and hour to have two digits
        month = str(month).zfill(2)
        day = str(day).zfill(2)
        hour = str(hour).zfill(2)

        # Construct the URL
        url = f"https://www.ncei.noaa.gov/data/geostationary-ir-channel-brightness-temperature-gridsat-b1/access/{year}/GRIDSAT-B1.{year}.{month}.{day}.{hour}.v02r01.nc"
        
        # Download the file
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the file
            with open(destination, 'wb') as f:
                f.write(response.content)
            print("File downloaded successfully!")
        else:
            print("Failed to download file.")

    destination = 'gridsatfile.nc'

    download_gridsat_nc(year, month, day, hour)

    # Load the NetCDF file
    dataset = xr.open_dataset(destination, decode_times=False)

    # Extract latitude, longitude, and infrared brightness temperature data
    lat = dataset['lat']
    lon = dataset['lon']
    brightness_temp = dataset['irwin_cdr']

    # Select a specific time slice (for example, the first time step)
    brightness_temp_slice = brightness_temp.isel(time=0)

    # Define the center latitude and longitude and the extent
    center_lat = cdy # Center latitude
    center_lon = cdx  # Center longitude
    extent = 8  # Extent in degrees

    # Calculate the bounds
    lat_min, lat_max = center_lat - extent, center_lat + extent
    lon_min, lon_max = center_lon - extent, center_lon + extent


    # Select data within the specified bounds
    selected_lat = lat[(lat >= lat_min) & (lat <= lat_max)]
    selected_lon = lon[(lon >= lon_min) & (lon <= lon_max)]
    selected_brightness_temp = brightness_temp_slice.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

    # Select data within the specified bounds
    selected_eye_temp = brightness_temp_slice.sel(lat=slice(center_lat-1, center_lat+1), lon=slice(center_lon-1, center_lon+1))

    # Find the maximum temperature
    max_temp = "{:.2f}".format(np.max(selected_eye_temp.values))

    def kelvin_to_celsius(kelvin_temp):
        celsius_temp = float(kelvin_temp) - 273.15
        return "{:.2f}".format(celsius_temp)


    # Create a map projection using Cartopy
    projection = ccrs.PlateCarree()

    # Plot the data on a map using pcolormesh
    plt.figure(figsize=(10, 8))  # Set plot size
    ax = plt.axes(projection=projection)
    pcolor = ax.pcolormesh(selected_lon, selected_lat, selected_brightness_temp, cmap='CMRmap', transform=projection)
    ax.coastlines()  # Add coastlines
    ax.set_xlabel('Longitude (degrees_east)')
    ax.set_ylabel('Latitude (degrees_north)')
    ax.set_title(f'GRIDSAT B1 Brightness Temperature IR on {str(hour).zfill(2)}:00 UTC {str(day).zfill(2)}/{str(month).zfill(2)}/{year}\nCentered at ({center_lat}, {center_lon}) +/- 5 degrees, Max eye temp = {kelvin_to_celsius(max_temp)} °C')
    gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gls.top_labels = False   # suppress top labels
    gls.right_labels = False  # suppress right labels
    cbar = plt.colorbar(pcolor, label='Brightness Temperature (Kelvin)')
    r = np.random.randint(1, 10)
    image_path = f'GRIDSAT{r}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)
    dataset.close()

    os.remove(destination)  


@bot.command(name='smap_custom')
async def smap_custom(ctx, cY:float, cX:float, nodeType:str):
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    from datetime import datetime
    import requests
    from io import BytesIO
    import numpy as np
    import os
    from matplotlib.lines import Line2D

    if cY < -90 or cY > 90 or cX > 179.99 or cX < -179.99:
        await ctx.send("Out of bounds!")
        return

    await ctx.send("Please hold as the data is generated.")
    nodeType = nodeType.upper()
    current_datetime = datetime.now()
    year = str(current_datetime.year)
    month = str(current_datetime.month).zfill(2)
    day = str(current_datetime.day).zfill(2)

    # Define the storm's coordinates
    storm_lat = cY  # Example latitude
    storm_lon = cX  # Example longitude
    storm_lon = storm_lon if storm_lon > 0 else 360 + storm_lon

    # Calculate latitude and longitude bounds for the bounding box
    lat_min = storm_lat - 10
    lat_max = storm_lat + 10
    lon_min = storm_lon - 10
    lon_max = storm_lon + 10

    url = f'https://data.remss.com/smap/wind/L3/v01.0/daily/NRT/{year}/RSS_smap_wind_daily_{year}_{month}_{day}_NRT_v01.0.nc'

    destination = f'ersst.v5.{year}{month}.nc'

    response = requests.get(url)
    with open(destination, 'wb') as file:
        file.write(response.content)

    await ctx.send("Generating data if available...")
    # Open the NetCDF file using xarray
    ds = xr.open_dataset(destination, decode_times=False)

    # Extract the wind variable
    wind = ds['wind']

    # Extract wind data within the bounding box
    wind_bounded = wind.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

    # Check if wind data is available within the bounding box
    if len(wind_bounded.lat) == 0 or len(wind_bounded.lon) == 0:
        print("No data available within the bounding box.")
    else:
        nodal = 0 if nodeType == 'ASC' else 1

        # Find the nearest latitude and longitude values in the dataset
        nearest_lat_index = np.abs(ds.lat.values - storm_lat).argmin()
        nearest_lon_index = np.abs(ds.lon.values - storm_lon).argmin()

        minute_data = ds.minute[nearest_lat_index, nearest_lon_index]
        print(minute_data)

        minute_data = ds.minute[nearest_lat_index, nearest_lon_index]
        print(minute_data)

        # Access the minute data for the nearest coordinate
        minute_data = ds.minute.isel(node=nodal).values[nearest_lat_index, nearest_lon_index]
        timePass=""

        # Check if minute data is available
        if np.isnan(minute_data):
            print("No minute data available for the nearest coordinate.")
            timePass += "NaN"
        else:
            # Print the minute data value
            print("Minute data value for the nearest coordinate:", minute_data)
            hr = str(int(minute_data) // 60).zfill(2)
            min = str(int(minute_data) % 60).zfill(2)
            timePass += f"{hr}{min} UTC"

        # Find the maximum wind value within the bounding box
        max_wind_value = wind_bounded.max()

        # Create the plot
        fig = plt.figure(figsize=(10, 6))
        ax = plt.axes(projection=ccrs.PlateCarree())

        # Plot wind data using pcolormesh
        mesh = ax.pcolormesh(wind.lon, wind.lat, (wind.isel(node=nodal))*1.944, transform=ccrs.PlateCarree(), cmap='gist_ncar', vmin=0, vmax=150)
        contour_17 = ax.contour(wind.lon, wind.lat, wind.isel(node=nodal), levels=[17], colors='black', transform=ccrs.PlateCarree())
        contour_25 = ax.contour(wind.lon, wind.lat, wind.isel(node=nodal), levels=[25], colors='green', transform=ccrs.PlateCarree())
        contour_32 = ax.contour(wind.lon, wind.lat, wind.isel(node=nodal), levels=[32], colors='red', transform=ccrs.PlateCarree())

        # Add coastlines
        ax.coastlines()

        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels=False   # suppress top labels
        gls.right_labels=False # suppress right labels

        # Set the extent of the plot to zoom into the bounding box
        ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

        legend_elements = [
        Line2D([0], [0], marker='_', color='k', label='34kt winds', markersize=10),
        Line2D([0], [0], marker='_', color='g', label='50kt winds', markersize=10),
        Line2D([0], [0], marker='_', color='r', label='64kt winds', markersize=10),
        ]

        # Add title
        plt.title('SMAP', loc='left')
        ax.legend(handles=legend_elements, loc='upper right')

        # Add colorbar
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.5, extend='both')
        cbar.set_label('Wind Speed (kts)')

        # Print the maximum wind value within the bounding box
        max_wind_value = max_wind_value.values.item()*1.944  # Get the raw value

        def oneMin(raw_SMAP):
            processed_SMAP = (362.644732816453 * raw_SMAP + 2913.62505913216) / 380.88384339523

            #Display output:
            processed_SMAP = "{:.2f}".format(processed_SMAP)
            return processed_SMAP

        plt.title(f'SMAP SFC Winds\nTime: {timePass}, {year}/{month}/{day}', loc='left', fontsize=7)
        plt.title(f"Maximum 10-min wind value: {max_wind_value:.2f} kts, 1-min: {oneMin(max_wind_value)} kt", loc='right', fontsize=8)

        # Show the plot
        r = np.random.randint(1, 10)
        image_path = f'Track_Map{r}.png'
        plt.savefig(image_path, format='png', bbox_inches='tight')
        plt.close()

        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

        os.remove(image_path)
        ds.close()

        os.remove(destination)  

@bot.command(name='pdolatest')
async def pdoLatest(ctx):
    import urllib3
    from bs4 import BeautifulSoup

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()
    
    url = "https://www.data.jma.go.jp/gmd/kaiyou/data/db/climate/pdo/pdo.txt"

    btk_data = fetch_url(url)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')
    pdoVal = lines[-2]

    month = {"01":"January", "02": "February", "03":"March", "04":"April",
             "05":"May", "06":"June", "07":"July", "08":"August",
             "09": "September", "10":"October", "11":"November", "12":"December"}
    await ctx.send(f"Latest PDO value for {month[pdoVal[5:7]]} {pdoVal[:4]} = {pdoVal[9:]} °C")

@bot.command(name='pdoplot')
async def pdoplot(ctx, yr:int):
    import pandas as pd
    import matplotlib.pyplot as plt
    from io import StringIO
    import requests
    import os

    if(yr < 1905 or yr > 2023):
        await ctx.send('Data either does not exist for this year or is yet to be created.')
        return

    # URL of the data
    url = 'https://www.data.jma.go.jp/gmd/kaiyou/data/db/climate/pdo/pdo.txt'

    # Fetch data from the URL
    response = requests.get(url)
    data = StringIO(response.text)

    # Read the data into a Pandas DataFrame
    df = pd.read_csv(data, delim_whitespace=True, skiprows=46, names=['Year_Month', 'PDO_Value'], parse_dates=[0])
    await ctx.send("Please hold as the image is created.")
    # Filter data for the year
    df_2023 = df[df['Year_Month'].dt.year == yr]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df_2023['Year_Month'], df_2023['PDO_Value'], marker='o', linestyle='-', color='b')

    # Add text annotations for each point
    for i, txt in enumerate(df_2023['PDO_Value']):
        plt.text(df_2023['Year_Month'].iloc[i], df_2023['PDO_Value'].iloc[i] + 0.05, round(txt, 2),
                horizontalalignment='center', verticalalignment='bottom', color='black')

    # Formatting
    plt.title(f'PDO Values in {yr}')
    plt.xlabel('Year and Month')
    plt.ylabel('PDO Value (°C)')
    plt.grid(True)
    # Adjust x-axis ticks to show every data point
    plt.xticks(df_2023['Year_Month'], rotation=45, ha='right')

    # Show the plot
    plt.tight_layout()
    image_path = f'PDO_plot_for{yr}.png'
    plt.savefig(image_path, format='png')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)  

@bot.command(name='ensoplot')
async def ensoplot(ctx, year:int):
    import pandas as pd
    import matplotlib.pyplot as plt
    import os

    if year < 1882 or year > 2023:
        await ctx.send("Data is either not available or is currently yet to be created.")
        return

    if year < 1950:
        # Load the 1882-2013 dataset
        df = pd.read_csv('enso_old.csv')
        # Filter the dataset for the given year
        df_year = df[df['year'] == year]
        # Exclude the last row
        df_year = df_year.iloc[:-1]
        # Plotting
        fig, ax = plt.subplots()
        ax.plot(df_year['month'], df_year['ENSO'], marker='o', label='ENSO', color='blue')
        plt.title(f'ENSO Data for {year} (1882-2023)')
        plt.xlabel('Month')
        plt.ylabel('ENSO (°C)')
        plt.grid(True)
    else:
        # Load the 1950-2023 dataset
        df = pd.read_csv('ENSO.csv', parse_dates=['Date'])
        # Filter the dataset for the given year
        df_year = df[df['Year'] == year]
        # Plotting
        fig, ax = plt.subplots()
        ax.plot(df_year['Month'], df_year['ONI'], marker='o', label='ONI', color='orange')
        plt.title(f'ENSO (ONI) Data for {year} (1882-2023)')
        plt.xlabel('Month')
        plt.ylabel('ENSO (ONI) (°C)')
        plt.grid(True)

    # Annotate each point with its exact value
    for i, txt in enumerate(df_year['ENSO' if year < 1950 else 'ONI']):
        plt.annotate(f'{txt:.2f}', (df_year['month'].iloc[i] if year < 1950 else df_year['Month'].iloc[i], txt), textcoords="offset points", xytext=(0, 5), ha='center')

    # Background color based on the sign of the values
    ax.axhspan(0, max(df_year['ENSO' if year < 1950 else 'ONI']), facecolor='red', alpha=0.1)
    ax.axhspan(min(df_year['ENSO' if year < 1950 else 'ONI']), 0, facecolor='blue', alpha=0.1)

    plt.xticks()
    plt.legend()
    plt.tight_layout()

    image_path = f'ENSO_plot_for{year}.png'
    plt.savefig(image_path, format='png')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)

@bot.command(name='iodplot')
async def iodplot(ctx, year:int):
    import pandas as pd
    import matplotlib.pyplot as plt
    import os

    if(year < 1870 or year > 2022):
        await ctx.send('Data either does not exist for this year or is yet to be created.')
        return

    Month = {1:"JAN", 2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC"}
    df = pd.read_csv('IOD.txt', delim_whitespace=True, header=None, names=['Year'] + [f'{Month[i]}' for i in range(1, 13)])

    data = df[df['Year'] == year].squeeze()
    
    months = [f'{Month[i]}' for i in range(1, 13)]
    values = data[1:]

    fig, ax = plt.subplots()

    bars = ax.bar(months, values)

    for bar in bars:
        if bar.get_height() < 0:
            bar.set_color('lightblue')
        else:
            bar.set_color('lightcoral')

    for i, value in enumerate(values):
        ax.text(i, value, f'{value:.3f}', ha='center', va='bottom' if value < 0 else 'top')

    plt.title(f'IOD Values for the Year {year} (1870-2022)')
    plt.xlabel('Month')
    plt.ylabel('IOD Value (°C)')
    plt.grid(axis='y')
    plt.tight_layout()

    image_path = f'IOD_plot_for{year}.png'
    plt.savefig(image_path, format='png')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)

@bot.command(name='meiplot')
async def meiplot(ctx, year:int):
    import pandas as pd
    import matplotlib.pyplot as plt
    import os

    if year < 1979 or year > 2023:
        await ctx.send("Data is either not available or is currently yet to be created.")
        return

    # Load the MEIv2 data from the text file
    file_path = 'meiv2.txt'
    df = pd.read_csv(file_path)
    # Filter data for the given year
    year_data = df[df['Year'] == year]

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot the data
    ax.plot(range(len(year_data.columns[1:])), year_data.values[0, 1:], marker='o', color='blue')

    # Annotate the values on the plot
    for i, txt in enumerate(year_data.values[0, 1:]):
        ax.annotate(f'{txt:.2f}', (i, txt), textcoords="offset points", xytext=(0, 5), ha='center')

    # Customize x-axis ticks
    ax.set_xticks(range(len(year_data.columns[1:])))
    ax.set_xticklabels(year_data.columns[1:])

    # Show the plot
    plt.title(f'MEIv2 Data for {year} (1979-2023)')
    plt.xlabel('Months')
    plt.ylabel('MEI Values')
    plt.grid(True)
    plt.tight_layout()

    image_path = f'MEI_plot_for{year}.png'
    plt.savefig(image_path, format='png')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)

@bot.command(name='tcprofile_ssd')
async def tcprofile_ssd(ctx, btkID:str, yr:str):
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter
    import matplotlib.dates as mdates
    import datetime
    import urllib3
    from bs4 import BeautifulSoup
    import os

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")

    if btkID[:2] in ['sh', 'wp', 'io']:
        btkUrl = f'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/JTWC/b{btkID}{yr}.dat'
    else:
        btkUrl = f'https://www.ssd.noaa.gov/PS/TROP/DATA/ATCF/NHC/b{btkID}{yr}.dat'

    btk_data = fetch_url(btkUrl)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')

    cdx, cdy, winds, status, timeCheck, pres, DateTime, r34 = [], [], [], [], [], [], [], []
    stormName = ""
    vmax = -1
    for line in lines:
        if line.strip():
            parameters = line.split(',')
            if parameters[6][-1] == 'S':
                cdy.append((float(parameters[6][:-1].strip()) / 10)*-1)
            else:
                cdy.append(float(parameters[6][:-1].strip()) / 10)
        
            if parameters[7][-1] == 'W':
                cdx.append((float(parameters[7][:-1].strip()) / 10)*-1)
            else:
                cdx.append(float(parameters[7][:-1].strip()) / 10)

            winds.append(int(parameters[8].strip()))
            if (vmax< winds[-1]):
                vmax = winds[-1]
            status.append(parameters[10].strip())
            timeCheck.append((parameters[2][-2:].strip()))
            date = parameters[2].strip()
            date = f'{date[:4]}-{date[4:6]}-{date[6:8]} {timeCheck[-1]}:00:00'
            DateTime.append(date)
            pres.append(int(parameters[9].strip()))
            r34.append(int(parameters[11].strip()))
            stormName = parameters[27].strip()

    #-------------------------------DEBUG INFORMATION-----------------------------------
    print(cdx, "\n", cdy, "\n", winds, "\n", status, "\n", timeCheck, "\n", r34, "\n", DateTime)
    #-----------------------------------------------------------------------------------

    # Convert string datetime to datetime objects
    DateTime = [datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in DateTime]

    # Create a figure and axis
    fig, ax1 = plt.subplots()

    # Plotting Winds on the primary Y-axis (left)
    ax1.set_xlabel('Date and Time')
    ax1.set_ylabel('Winds (Kts)', color='tab:blue')
    ax1.plot(DateTime, winds, color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Create a secondary Y-axis (right) for Pressure
    ax2 = ax1.twinx()
    ax2.set_ylabel('Pressure (hPa)', color='tab:red')
    ax2.plot(DateTime, pres, color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Formatting date on the X-axis
    date_form = DateFormatter('%Y-%m-%d')
    ax1.xaxis.set_major_formatter(date_form)
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=24))

    # Rotate and align the date labels so they look better
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right")

    def calc_ACE(winds, timeCheck):
        ace = 0
        aceList = []
        for i in range(len(winds)):
            if(winds[i] == ' '):
                continue
            time = int(timeCheck[i]) % 6 #If it is synoptic time and meets...
            if(time==0 and r34[i] == 34 and status[i] not in ['DB', 'LO', 'WV', 'EX']): 
                ace += (int(winds[i]) ** 2) / 10000
                aceList.append(ace)
        print(aceList)
        return "{:.4f}".format(ace)

    # Show the plot
    plt.grid()
    plt.title(f'Intensity profile for {btkID}{yr}')
    plt.title(f'VMAX: {vmax} Kts', loc='left', fontsize=9)
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right', fontsize=9)
    plt.tight_layout()

    image_path = f'{btkID}_{yr}_Intensity_Profile.png'
    plt.savefig(image_path, format='png')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)  

@bot.command(name='tcprofile')
async def tcprofile(ctx, btkID:str, yr:str):
    import csv
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter
    import matplotlib.dates as mdates
    from datetime import datetime
    import os

    btkID = btkID.upper()
    if btkID == 'BENTO':
        btkID = 'BENTOJANA'
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'VICKY 2020', 'JOYCE 2018', 'GORDON 1979', 'BENI 2003', 'MARK 1992', 'NADINE 1978',
                  'WINNIE 1978', 'HARVEY 2005', 'FREDA 1981', 'CARMEN 1974']
    check = f"{btkID} {yr}"
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    if(btkID == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    #Load in the loops for finding the latitude and longitude...
    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, winds, status, timeCheck, DateTime, pres = [], [], [], [], [], [], []
    storm_name = ""
    s_ID = ""
    vmax = -999
    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r00.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]):
                    DateTime.append(lines[6])
                    s_ID = lines[18]
                    cdx.append(lines[20])
                    cdy.append(lines[19])
                    if int(yr) < 2002:
                        if lines[23] == ' ':
                            winds.append(15)
                        else:
                            winds.append(int(lines[23]))
                        if lines[11] == ' ':
                            pres.append(1010)
                        else:
                            pres.append(int(lines[11]))
                        if (vmax< int(winds[-1])):
                            vmax = int(winds[-1])
                    else:
                        if lines[23] == ' ':
                            winds.append(15)
                        else:
                            winds.append(int(lines[23]))
                        if lines[24] == ' ':
                            pres.append(1010)
                        else:
                            pres.append(int(lines[24]))
                        if (vmax< int(winds[-1])):
                            vmax = int(winds[-1])
                    status.append(lines[22])
                    timeCheck.append(lines[6][-8:-6])
                    storm_name = lines[5]
        
    #-------------------------------DEBUG INFORMATION-----------------------------------
    print(DateTime, "\n", winds, "\n", pres, "\n", storm_name)
    #-----------------------------------------------------------------------------------

    # Convert string datetime to datetime objects

    DateTimePlot = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in DateTime]

    # Create a figure and axis
    fig, ax1 = plt.subplots()

    # Plotting Winds on the primary Y-axis (left)
    ax1.set_xlabel('Date and Time')
    ax1.set_ylabel('Winds (Kts)', color='tab:blue')
    ax1.plot(DateTimePlot, winds, color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    plt.grid(True)
    if int(yr) > 2002:
        # Create a secondary Y-axis (right) for Pressure
        ax2 = ax1.twinx()
        ax2.set_ylabel('Pressure (hPa)', color='tab:red')
        ax2.plot(DateTimePlot, pres, color='tab:red')
        ax2.tick_params(axis='y', labelcolor='tab:red')

    # Formatting date on the X-axis
    date_form = DateFormatter('%Y-%m-%d')
    ax1.xaxis.set_major_formatter(date_form)
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=24))

    #Building the function that calculates ACE...
    def calc_ACE(winds, timeCheck):
        ace = 0
    
        for i in range(len(winds)):
            if(winds[i] == ' '):
                continue
            time = int(timeCheck[i]) % 6
            if(time==0 and int(winds[i]) >= 34 and status[i] not in ['DB', 'LO', 'WV', 'EX']): #If it is synoptic time and meets...
                ace += (int(winds[i]) ** 2) / 10000
        return "{:.4f}".format(ace)

    # Rotate and align the date labels so they look better
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right")

    # Show the plot
    plt.title(f'{btkID} {yr}', loc='center')
    plt.title(f'VMAX: {vmax} Kts', loc='left', fontsize=9)
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right', fontsize=9)
    plt.tight_layout()
    
    image_path = f'{btkID}_{yr}_Intensity_Profile.png'
    plt.savefig(image_path, format='png')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)  

@bot.command(name = 'oldibtracs')
async def oldibtracs(ctx, btkID:str, yr:str):
    import csv
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.lines import Line2D
    import os
    btkID = btkID.upper()
    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    
    print(f"Command received from server: {ctx.guild.name}")
    #Load in the loops for finding the latitude and longitude...
    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, winds, status, timeCheck, DateTime = [], [], [], [], [], []
    storm_name = ""
    s_ID = ""
    idl = False
    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r00.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]) or btkID == lines[0]:
                    DateTime.append(lines[6])
                    s_ID = lines[18]
                    cdx.append(lines[9])
                    if(cdx[-1] == ' '):
                        pass
                    elif(float(cdx[-1]) < -178 or float(cdx[-1]) > 178):
                        idl = True
                    cdy.append(lines[8])
                    timeCheck.append(lines[6][-8:-6])
                    
        
    
    #-------------------------------DEBUG INFORMATION-----------------------------------
    print(cdx, "\n", cdy, "\n", timeCheck, "\n", storm_name)
    #-----------------------------------------------------------------------------------
    await ctx.send("System located in database, generating track...")

    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

    ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    maxLat, minLat, maxLong, minLong = -999, 999, -999, 999
    vmax, statMaxIndx = 0, 0

    #Plotting the markers...
    for i in range(0, len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ':
            continue
        
        if idl == True:
            coord_x, coord_y = float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180, float(cdy[i])
        else:
            coord_x, coord_y = float(cdx[i]), float(cdy[i])

        #Setup for finding bounding box...
        if(maxLat < coord_y):
            maxLat = coord_y
        if(minLat > coord_y):
            minLat = coord_y
        if(maxLong < coord_x):
            maxLong = coord_x
        if(minLong > coord_x):
            minLong = coord_x 
        

        if(int(timeCheck[i]) % 6  == 0):
            #Mark scatter plots...
            plt.scatter(coord_x, coord_y, color='#444764', marker='o')

    #Setting the coordinates for the bounding box...
    center_x = (minLong + maxLong)/2
    center_y = (minLat + maxLat)/2

    center_width = abs(maxLong - minLong)
    center_height = abs(maxLat - minLat)

    ratio = (center_height/center_width)
    print(ratio)
    if ratio < 0.3:
        ax.set_xlim(center_x-center_width, center_x+center_width)
        ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
    elif ratio > 0.7:
        ax.set_xlim(center_x-(center_height), center_x+(center_height))
        ax.set_ylim(center_y-center_height, center_y+center_height)
    else:
        ax.set_xlim(center_x-center_width, center_x+center_width)
        ax.set_ylim(center_y-center_height, center_y+center_height)

    #Defining the legend box for the plot...
    legend_elements = [
                    Line2D([0], [0], marker='o', color='w', label='TC Marked Path',markerfacecolor='#444764', markersize=10),
    ]

    #Plotting the TC Path...
    LineX = []
    LineY = []

    for i in range(len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ':
            continue
        if idl == True:
            LineX.append(float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180)
        else:
            LineX.append(float(cdx[i]))
        LineY.append(float(cdy[i]))

    plt.plot(LineX, LineY, color="k", linestyle="--")
    plt.text(LineX[0], LineY[0]+0.5, f'{DateTime[0]}')
    plt.text(LineX[len(LineX)-1], LineY[len(LineX)-1]+0.5, f'{DateTime[len(LineX)-1]}')

    #Applying final touches...
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'{s_ID} {storm_name}')
    ax.legend(handles=legend_elements, loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    # Adjust spacing above and below the plot
    image_path = f'Track_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)  


@bot.command(name='trackgen_hurdat')
async def trackgen_hurdat(ctx, url:str):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.lines import Line2D
    import urllib3
    from bs4 import BeautifulSoup
    import os

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()


    btk_data = fetch_url(url)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')

    cdx, cdy, winds, status, timeCheck, pres, DateTime, r34 = [], [], [], [], [], [], [], []
    stormName = ""
    idl = False
    for line in lines:
        if line.strip():
            stormData = line.split(',')

            #Checking Longitudinal Hemisphere...
            if(stormData[5][-1] == 'W'):
                cdx.append(float(stormData[5][:-1].strip())*-1)
            else:
                cdx.append(float(stormData[5][:-1].strip()))
            if(cdx[-1] == ' '):
                    pass
            elif(float(cdx[-1]) < -175 or float(cdx[-1]) > 175):
                idl = True
            #Checking Latitudinal Hemisphere...
            if(stormData[4][-1] == 'S'):
                cdy.append(float(stormData[4][:-1].strip())*-1)
            else:
                cdy.append(float(stormData[4][:-1].strip()))
            
            status.append(stormData[3].strip())
            winds.append(int(stormData[6].strip()))
            presVal = stormData[7].strip()
            pres.append(int(presVal) if presVal != '' else 1010)
            stormData[1] = stormData[1].strip() #Bugfix
            timeCheck.append(int(stormData[1][:2]))
        
    #---------------------------DEBUG INFORMATION--------------------------------
    print(cdx, "\n", cdy, "\n", winds, '\n', pres, '\n', timeCheck, '\n', status)
    #----------------------------------------------------------------------------
    print(f"Command received from server: {ctx.guild.name}")
    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

    ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    maxLat, minLat, maxLong, minLong = -999, 999, -999, 999
    vmax, pmin = 0, 9999

    #Plotting the markers...
    for i in range(len(cdx)):
        if idl == True:
            coord_x, coord_y = float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180, float(cdy[i])
        else:
            coord_x, coord_y = float(cdx[i]), float(cdy[i])
        wind = int(winds[i])

        #Setup for finding bounding box...
        if(maxLat < coord_y):
            maxLat = coord_y
        if(minLat > coord_y):
            minLat = coord_y
        if(maxLong < coord_x):
            maxLong = coord_x
        if(minLong > coord_x):
            minLong = coord_x 
        
        #Setup for displaying VMAX as well as peak Status...
        if vmax < wind and status[i] not in ['EX', 'DB', 'WV', 'LO', 'MD']:
            vmax = wind
        if pmin > pres[i]:
            pmin = pres[i]
        
        if(int(timeCheck[i]) % 6  == 0):
            #Mark scatter plots...
            if status[i] in ['DB', 'WV', 'LO', 'MD']:
                plt.scatter(coord_x, coord_y, color='#444764', marker='^', zorder=3)
            elif status[i] == 'EX':
                if int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='^', zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='^', zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='^', zorder=3)
            elif status[i] == 'SS':
                plt.scatter(coord_x, coord_y, color='g', marker='s', zorder=3)
            elif status[i] == 'SD':
                plt.scatter(coord_x, coord_y, color='b', marker='s', zorder=3)
            else:
                if int(wind) >= 137:
                    plt.scatter(coord_x, coord_y, color='m', marker='o', zorder=3)
                elif int(wind) >= 112:
                    plt.scatter(coord_x, coord_y, color='r', marker='o', zorder=3)
                elif int(wind) >= 96:
                    plt.scatter(coord_x, coord_y, color='#ff5908', marker='o', zorder=3)
                elif int(wind) >= 81:
                    plt.scatter(coord_x, coord_y, color='#ffa001', marker='o', zorder=3)
                elif int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='o', zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='o', zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='o', zorder=3)

    #Setting the coordinates for the bounding box...
    center_x = (minLong + maxLong)/2
    center_y = (minLat + maxLat)/2

    center_width = abs(maxLong - minLong)
    center_height = abs(maxLat - minLat)
    if center_width==0 and center_height==0:
        ax.set_xlim(center_x-10, center_x+10)
        ax.set_ylim(center_y-10, center_y+10)
    else:
        ratio = (center_height/center_width)
        print(ratio)
        if ratio < 0.3:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
        elif ratio > 0.7:
            ax.set_xlim(center_x-(center_height), center_x+(center_height))
            ax.set_ylim(center_y-center_height, center_y+center_height)
        else:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-center_height, center_y+center_height)

    #Defining the legend box for the plot...
    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='Non-Tropical',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='Sub-Tropical',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Tropical Depression',markerfacecolor='b', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Tropical Storm',markerfacecolor='g', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 1',markerfacecolor='#ffff00', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 2',markerfacecolor='#ffa001', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 3',markerfacecolor='#ff5908', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 4',markerfacecolor='r', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 5',markerfacecolor='m', markersize=10),
    ]

    #Building the function that calculates ACE...
    def calc_ACE(winds, timeCheck):
        ace = 0
    
        for i in range(len(winds)):
            if(winds[i] == ' '):
                continue
            time = int(timeCheck[i]) % 6
            if(time==0 and int(winds[i]) >= 34 and status[i] not in ['DB', 'LO', 'WV', 'EX']): #If it is synoptic time and meets...
                ace += (int(winds[i]) ** 2) / 10000
        return "{:.4f}".format(ace)

    #Plotting the TC Path...
    LineX = []
    LineY = []

    for i in range(len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ':
            continue
        if idl == True:
            LineX.append(float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180)
        else:
            LineX.append(float(cdx[i]))
        LineY.append(float(cdy[i]))

    plt.plot(LineX, LineY, color="k", linestyle="-")

    #Applying final touches...
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Peak Intensity: {vmax} Kts, {pmin} hPa', loc='left')
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right')
    ax.legend(handles=legend_elements, loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    # Adjust spacing above and below the plot
    

    image_path = f'Track_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)  

@bot.command(name='trackgen_atcf')
async def trackgen_atcf(ctx, url:str):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.lines import Line2D
    import urllib3
    from bs4 import BeautifulSoup
    import os

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()


    btk_data = fetch_url(url)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')
    idl = False
    cdx, cdy, winds, status, timeCheck, pres, DateTime, r34 = [], [], [], [], [], [], [], []
    stormName = ""

    for line in lines:
        if line.strip():
            stormData = line.split(',')

            #Checking Longitudinal Hemisphere...
            if(stormData[7][-1] == 'W'):
                cdx.append((float(stormData[7][:-1].strip())/10)*-1)
            else:
                cdx.append(float(stormData[7][:-1].strip())/10)
            if(cdx[-1] == ' '):
                pass
            elif(float(cdx[-1]) < -175 or float(cdx[-1]) > 175):
                idl = True
            #Checking Latitudinal Hemisphere...
            if(stormData[6][-1] == 'S'):
                cdy.append((float(stormData[6][:-1].strip())/10)*-1)
            else:
                cdy.append(float(stormData[6][:-1].strip())/10)
            
            status.append(stormData[10].strip())
            winds.append(int(stormData[8].strip()))
            presVal = stormData[9].strip()
            pres.append(int(presVal) if presVal != '' else 1010)
            stormData[2] = stormData[2].strip() #Bugfix
            timeCheck.append(int(stormData[2][-2:]))
        
    #---------------------------DEBUG INFORMATION--------------------------------
    print(cdx, "\n", cdy, "\n", winds, '\n', pres, '\n', timeCheck, '\n', status)
    #----------------------------------------------------------------------------
    print(f"Command received from server: {ctx.guild.name}")
    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

    ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    maxLat, minLat, maxLong, minLong = -999, 999, -999, 999
    vmax, pmin = 0, 9999

    #Plotting the markers...
    for i in range(len(cdx)):
        if idl == True:
            coord_x, coord_y = float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180, float(cdy[i])
        else:
            coord_x, coord_y = float(cdx[i]), float(cdy[i])
        wind = int(winds[i])

        #Setup for finding bounding box...
        if(maxLat < coord_y):
            maxLat = coord_y
        if(minLat > coord_y):
            minLat = coord_y
        if(maxLong < coord_x):
            maxLong = coord_x
        if(minLong > coord_x):
            minLong = coord_x 
        
        #Setup for displaying VMAX as well as peak Status...
        if vmax < wind and status[i] not in ['EX', 'DB', 'WV', 'LO', 'MD']:
            vmax = wind
        if pmin > pres[i]:
            pmin = pres[i]
        
        if(int(timeCheck[i]) % 6  == 0):
            #Mark scatter plots...
            if status[i] in ['DB', 'WV', 'LO', 'MD']:
                plt.scatter(coord_x, coord_y, color='#444764', marker='^', zorder=3)
            elif status[i] == 'EX':
                if int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='^', zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='^', zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='^', zorder=3)
            elif status[i] == 'SS':
                plt.scatter(coord_x, coord_y, color='g', marker='s', zorder=3)
            elif status[i] == 'SD':
                plt.scatter(coord_x, coord_y, color='b', marker='s', zorder=3)
            else:
                if int(wind) >= 137:
                    plt.scatter(coord_x, coord_y, color='m', marker='o', zorder=3)
                elif int(wind) >= 112:
                    plt.scatter(coord_x, coord_y, color='r', marker='o', zorder=3)
                elif int(wind) >= 96:
                    plt.scatter(coord_x, coord_y, color='#ff5908', marker='o', zorder=3)
                elif int(wind) >= 81:
                    plt.scatter(coord_x, coord_y, color='#ffa001', marker='o', zorder=3)
                elif int(wind) >= 64:
                    plt.scatter(coord_x, coord_y, color='#ffff00', marker='o', zorder=3)
                elif int(wind) >= 34:
                    plt.scatter(coord_x, coord_y, color='g', marker='o', zorder=3)
                else:
                    plt.scatter(coord_x, coord_y, color='b', marker='o', zorder=3)

    #Setting the coordinates for the bounding box...
    center_x = (minLong + maxLong)/2
    center_y = (minLat + maxLat)/2

    center_width = abs(maxLong - minLong)
    center_height = abs(maxLat - minLat)

    if center_width==0 and center_height==0:
        ax.set_xlim(center_x-10, center_x+10)
        ax.set_ylim(center_y-10, center_y+10)
    else:
        ratio = (center_height/center_width)
        print(ratio)
        if ratio < 0.3:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
        elif ratio > 0.7:
            ax.set_xlim(center_x-(center_height), center_x+(center_height))
            ax.set_ylim(center_y-center_height, center_y+center_height)
        else:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-center_height, center_y+center_height)

    #Defining the legend box for the plot...
    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='Non-Tropical',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='Sub-Tropical',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Tropical Depression',markerfacecolor='b', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Tropical Storm',markerfacecolor='g', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 1',markerfacecolor='#ffff00', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 2',markerfacecolor='#ffa001', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 3',markerfacecolor='#ff5908', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 4',markerfacecolor='r', markersize=10),
                    Line2D([0], [0], marker='o', color='w', label='Category 5',markerfacecolor='m', markersize=10),
    ]

    #Building the function that calculates ACE...
    def calc_ACE(winds, timeCheck):
        ace = 0
    
        for i in range(len(winds)):
            if(winds[i] == ' '):
                continue
            time = int(timeCheck[i]) % 6
            if(time==0 and int(winds[i]) >= 34 and status[i] not in ['DB', 'LO', 'WV', 'EX']): #If it is synoptic time and meets...
                ace += (int(winds[i]) ** 2) / 10000
        return "{:.4f}".format(ace)

    #Plotting the TC Path...
    LineX = []
    LineY = []

    for i in range(len(cdx)):
        if cdx[i] == ' ' or cdy[i] == ' ':
            continue
        if idl == True:
            LineX.append(float(cdx[i])+180 if float(cdx[i])<0 else float(cdx[i])-180)
        else:
            LineX.append(float(cdx[i]))
        LineY.append(float(cdy[i]))

    plt.plot(LineX, LineY, color="k", linestyle="-")

    #Applying final touches...
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Peak Intensity: {vmax} Kts, {pmin} hPa', loc='left')
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right')
    ax.legend(handles=legend_elements, loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    # Adjust spacing above and below the plot
    

    image_path = f'Track_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)

@bot.command(name='jordan')
async def jordan(ctx, height:float):
    Pc = 0

    Pc = 645 + 0.115 * height
    Pc = "{:.2f}".format(Pc)

    print("The extrapolated pressure:", Pc, "mb")
    await ctx.send(f"The extrapolated pressure: {Pc} mb")

@bot.command(name='dist')
async def dist(ctx, x1:float, y1:float, x2:float, y2:float):
    import math

    #Convert to radians
    x1 *= 0.0174533
    y1 *= 0.0174533
    x2 *= 0.0174533
    y2 *= 0.0174533

    radius = 6378.137 #Assumed radius of the planet

    #Apply the equation:
    delY = y2 - y1
    d_km = radius * math.acos(math.sin(x1) * math.sin(x2) + math.cos(x1) * math.cos(x2) * math.cos(delY))

    d_nm = d_km * 0.539957 #Finding the equivalent in nautical miles

    #Print the output:
    d_km = "{:.2f}".format(d_km)
    d_nm = "{:.2f}".format(d_nm)
    await ctx.send(f"Distance in km: {d_km} km, in nautical miles: {d_nm} nm")

@bot.command(name='mslp')
async def mslp(ctx, altitude:float, temperature:float, pressure:float):
    p0 = pressure * (1 - ((0.0065 * altitude)/(temperature + 273.15 + 0.0065 * altitude))) ** (-5.257)

    #Present the output in a readable manner:
    pr = "{:.2f}".format(p0)
    await ctx.send(f"The equivalent sea level pressure: {pr} mb/hPa")

@bot.command(name='ascat')
async def ascat(ctx, AWS:float):
    DWS = 0 #Approx value for true winds, denoted as Dropsonde Wind Speed.

    #The formula works in m/s values, so we will first convert AWS to m/s:
    AWS = AWS / 1.94384

    #Applying the regression formula created by Chou et. al 2013:
    DWS = (0.014 * AWS ** 2) + (0.821 * AWS) + 0.961

    #We will now convert the m/s output to kts:
    DWS = DWS * 1.94384

    #Present the output in a readable manner:
    DWS = "{:.2f}".format(DWS)
    await ctx.send(f"Warning: Please remember that this is meant for 25km resolution ASCAT and that you should only do it for visible barbs. This is statistically taken from Chou et al. 2013 and is not meant to be used completely at face value.")
    await ctx.send(f"The adjusted representative windspeed: {DWS} kt")

@bot.command(name='hursat')
async def hursat(ctx, btkID:str, yr:str):
    import csv

    btkID = btkID.upper()
    if btkID == 'BENTO':
        btkID = 'BENTOJANA'
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'VICKY 2020', 'JOYCE 2018', 'GORDON 1979', 'BENI 2003', 'MARK 1992', 'NADINE 1978',
                  'WINNIE 1978', 'HARVEY 2005', 'FREDA 1981', 'POLLY 1970', 'LOUISE 1970', 'LUCY 1962', 'CARMEN 1974']
    check = f"{btkID} {yr}"
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    if(btkID == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    #Load in the loops for finding the latitude and longitude...
    IBTRACS_ID = f"{btkID}{yr}"
    hursat_ID = ""
    with open('ibtracs.ALL.list.v04r00.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                    #If IBTRACS ID matches the ID on the script...
                    if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]):
                        hursat_ID = lines[0]
                        break

    url = f"https://www1.ncdc.noaa.gov/pub/data/satellite/hursat/{yr}/{hursat_ID}/"
    await ctx.send(url)

@bot.command(name='shear')
async def shear(ctx, basin:str):
    import requests
    from io import BytesIO

    basin = basin.lower()
    url = ""
    if basin == "westpac":
        url += "https://tropic.ssec.wisc.edu/real-time/westpac/winds/wgmsshr.GIF?28183947292"
    elif basin == "eastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/eastpac/winds/wg9shr.GIF?28183947292"
    elif basin == "seastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/seastpac/winds/wg10sshr.GIF?28183947292"
    elif basin == "atlantic":
        url += "https://tropic.ssec.wisc.edu/real-time/atlantic/winds/wg8shr.GIF?28183947292"
    elif basin == "europe":
        url += "https://tropic.ssec.wisc.edu/real-time/europe/winds/wm7shr.GIF?28183947292"
    elif basin == "indian":
        url += "https://tropic.ssec.wisc.edu/real-time/indian/winds/wm5shr.GIF?28183947292"
    elif basin == "austwest":
        url += "https://tropic.ssec.wisc.edu/real-time/austwest/winds/wgmsshr.GIF?28183947292"
    elif basin == "austeast":
        url += "https://tropic.ssec.wisc.edu/real-time/austeast/winds/wgmsshr.GIF?28183947292"
    else:
        await ctx.send("The given basin is not valid! Valid basins are [westpac, eastpac, seastpac, atlantic, europe, indian, austwest, austeast]")
        return
    
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='ulir')
async def ulir(ctx, basin:str):
    import requests
    from io import BytesIO

    basin = basin.lower()
    url = ""
    if basin == "westpac":
        url += "https://tropic.ssec.wisc.edu/real-time/westpac/winds/wgmswvir.GIF?28183947292"
    elif basin == "eastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/eastpac/winds/wg9wvir.GIF?28183947292"
    elif basin == "seastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/seastpac/winds/wg10swvir.GIF?28183947292"
    elif basin == "atlantic":
        url += "https://tropic.ssec.wisc.edu/real-time/atlantic/winds/wg8wvir.GIF?28183947292"
    elif basin == "europe":
        url += "https://tropic.ssec.wisc.edu/real-time/europe/winds/wm7wvir.GIF?28183947292"
    elif basin == "indian":
        url += "https://tropic.ssec.wisc.edu/real-time/indian/winds/wm5wvir.GIF?28183947292"
    elif basin == "austwest":
        url += "https://tropic.ssec.wisc.edu/real-time/austwest/winds/wgmswvir.GIF?28183947292"
    elif basin == "austeast":
        url += "https://tropic.ssec.wisc.edu/real-time/austeast/winds/wgmswvir.GIF?28183947292"
    else:
        await ctx.send("The given basin is not valid! Valid basins are [westpac, eastpac, seastpac, atlantic, europe, indian, austwest, austeast]")
        return
    
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='llir')
async def llir(ctx, basin:str):
    import requests
    from io import BytesIO

    basin = basin.lower()
    url = ""
    if basin == "westpac":
        url += "https://tropic.ssec.wisc.edu/real-time/westpac/winds/wgmsir.GIF?28183947292"
    elif basin == "eastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/eastpac/winds/wg9ir.GIF?28183947292"
    elif basin == "seastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/seastpac/winds/wg10sir.GIF?28183947292"
    elif basin == "atlantic":
        url += "https://tropic.ssec.wisc.edu/real-time/atlantic/winds/wg8ir.GIF?28183947292"
    elif basin == "europe":
        url += "https://tropic.ssec.wisc.edu/real-time/europe/winds/wm7ir.GIF?28183947292"
    elif basin == "indian":
        url += "https://tropic.ssec.wisc.edu/real-time/indian/winds/wm5ir.GIF?28183947292"
    elif basin == "austwest":
        url += "https://tropic.ssec.wisc.edu/real-time/austwest/winds/wgmsir.GIF?28183947292"
    elif basin == "austeast":
        url += "https://tropic.ssec.wisc.edu/real-time/austeast/winds/wgmsir.GIF?28183947292"
    else:
        await ctx.send("The given basin is not valid! Valid basins are [westpac, eastpac, seastpac, atlantic, europe, indian, austwest, austeast]")
        return
    
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='uldiv')
async def uldiv(ctx, basin:str):
    import requests
    from io import BytesIO
    basin = basin.lower()
    url = ""
    if basin == "westpac":
        url += "https://tropic.ssec.wisc.edu/real-time/westpac/winds/wgmsdvg.GIF?28183947292"
    elif basin == "eastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/eastpac/winds/wg9dvg.GIF?28183947292"
    elif basin == "seastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/seastpac/winds/wg10sdvg.GIF?28183947292"
    elif basin == "atlantic":
        url += "https://tropic.ssec.wisc.edu/real-time/atlantic/winds/wg8dvg.GIF?28183947292"
    elif basin == "europe":
        url += "https://tropic.ssec.wisc.edu/real-time/europe/winds/wm7dvg.GIF?28183947292"
    elif basin == "indian":
        url += "https://tropic.ssec.wisc.edu/real-time/indian/winds/wm5dvg.GIF?28183947292"
    elif basin == "austwest":
        url += "https://tropic.ssec.wisc.edu/real-time/austwest/winds/wgmsdvg.GIF?28183947292"
    elif basin == "austeast":
        url += "https://tropic.ssec.wisc.edu/real-time/austeast/winds/wgmsdvg.GIF?28183947292"
    else:
        await ctx.send("The given basin is not valid! Valid basins are [westpac, eastpac, seastpac, atlantic, europe, indian, austwest, austeast]")
        return
    
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='llconv')
async def llconv(ctx, basin:str):
    import requests
    from io import BytesIO
    basin = basin.lower()
    url = ""
    if basin == "westpac":
        url += "https://tropic.ssec.wisc.edu/real-time/westpac/winds/wgmsconv.GIF?28183947292"
    elif basin == "eastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/eastpac/winds/wg9conv.GIF?28183947292"
    elif basin == "seastpac":
        url += "https://tropic.ssec.wisc.edu/real-time/seastpac/winds/wg10sconv.GIF?28183947292"
    elif basin == "atlantic":
        url += "https://tropic.ssec.wisc.edu/real-time/atlantic/winds/wg8conv.GIF?28183947292"
    elif basin == "europe":
        url += "https://tropic.ssec.wisc.edu/real-time/europe/winds/wm7conv.GIF?28183947292"
    elif basin == "indian":
        url += "https://tropic.ssec.wisc.edu/real-time/indian/winds/wm5conv.GIF?28183947292"
    elif basin == "austwest":
        url += "https://tropic.ssec.wisc.edu/real-time/austwest/winds/wgmsconv.GIF?28183947292"
    elif basin == "austeast":
        url += "https://tropic.ssec.wisc.edu/real-time/austeast/winds/wgmsconv.GIF?28183947292"
    else:
        await ctx.send("The given basin is not valid! Valid basins are [westpac, eastpac, seastpac, atlantic, europe, indian, austwest, austeast]")
        return
    
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='vort')
async def vort(ctx, basin:str, hpa:int):
    import requests
    from io import BytesIO
    basin = basin.lower()
    if hpa not in [200, 500, 700, 850, 925]:
        await ctx.send("Not a valid value. Accepted values are [200, 500, 700, 850, 925] mb/hPa.")
        return
    keyVal = {200:"vor1", 500:"vor2", 700:"vor3", 850:"vor", 925:"vor5"}
    url = ""
    if basin == "westpac":
        url += f"https://tropic.ssec.wisc.edu/real-time/westpac/winds/wgms{keyVal[hpa]}.GIF?28183947292"
    elif basin == "eastpac":
        url += f"https://tropic.ssec.wisc.edu/real-time/eastpac/winds/wg9{keyVal[hpa]}.GIF?28183947292"
    elif basin == "seastpac":
        url += f"https://tropic.ssec.wisc.edu/real-time/seastpac/winds/wg10s{keyVal[hpa]}.GIF?28183947292"
    elif basin == "atlantic":
        url += f"https://tropic.ssec.wisc.edu/real-time/atlantic/winds/wg8{keyVal[hpa]}.GIF?28183947292"
    elif basin == "europe":
        url += f"https://tropic.ssec.wisc.edu/real-time/europe/winds/wm7{keyVal[hpa]}.GIF?28183947292"
    elif basin == "indian":
        url += f"https://tropic.ssec.wisc.edu/real-time/indian/winds/wm5{keyVal[hpa]}.GIF?28183947292"
    elif basin == "austwest":
        url += f"https://tropic.ssec.wisc.edu/real-time/austwest/winds/wgms{keyVal[hpa]}.GIF?28183947292"
    elif basin == "austeast":
        url += f"https://tropic.ssec.wisc.edu/real-time/austeast/winds/wgms{keyVal[hpa]}.GIF?28183947292"
    else:
        await ctx.send("The given basin is not valid! Valid basins are [westpac, eastpac, seastpac, atlantic, europe, indian, austwest, austeast]")
        return
    
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='gibbs')
async def gibbs(ctx, sat:str, type:str, hour:int, day:int, month:int, yr:int):
    import requests
    from io import BytesIO

    hour = str(hour).zfill(2)
    day = str(day).zfill(2)
    month = str(month).zfill(2)
    sat = sat.upper()
    type = type.upper()
    
    url = f"https://www.ncdc.noaa.gov/gibbs/image/{sat}/{type}/{yr}-{month}-{day}-{hour}"
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")        
    if response.status_code == 200:
        image_data = BytesIO(response.content)
        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")
        await ctx.send("For reference, go to this link: https://inventory.ssec.wisc.edu/inventory/#calendar")
        await ctx.send(f"And check the date also: https://www.ncdc.noaa.gov/gibbs/availability/{yr}-{month}-{day}")

@bot.command(name='satcon')
async def satcon(ctx, id:str, yr:str):
    import requests
    from io import BytesIO
    id = id.upper()
    if int(yr) < 2012:
        url = f"https://tropic.ssec.wisc.edu/real-time/satcon/archive/{yr}/{id}_wind.gif"
    elif int(yr) <= 2020:
        url = f"https://tropic.ssec.wisc.edu/real-time/satcon/archive/{yr}/{yr}{id}_wind_ssmis.gif"
    else:   
        url = f"https://tropic.ssec.wisc.edu/real-time/satcon/archive/{yr}/{yr}{id}_wind.png"
    
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")


@bot.command(name='dprint')
async def dprint(ctx, id:str, yr:str):
    import requests
    from io import BytesIO
    id = id.upper()
    url = f"https://tropic.ssec.wisc.edu/real-time/DPRINT/{yr}/{yr}_{id}_intensity_plot.png?28183947292"

    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='dmint')
async def dmint(ctx, id:str, yr:str):
    import requests
    from io import BytesIO
    id = id.upper()
    url = f"https://tropic.ssec.wisc.edu/real-time/DMINT/{yr}/{yr}_{id}_intensity_plot.png?28183947292"

    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='adt')
async def adt(ctx, atcfID:str, yr:str):
    atcfID = atcfID.upper()

    url = f"https://tropic.ssec.wisc.edu/real-time/adt/archive{yr}/{atcfID}-list.txt"
    await ctx.send(f"ADT history file for {atcfID} {yr}:")
    await ctx.send(url)

@bot.command(name='archer')
async def archer(ctx, id:str, yr:str):
    import requests

    id = id.upper()
    url = f"https://tropic.ssec.wisc.edu/real-time/archerOnline/cyclones/{yr}_{id}/web/track.png"

    response = requests.get(url)

    if response.status_code == 200:
        await ctx.send(url)
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='dvorak_eye')
async def dvorak_eye(ctx, embed:str, eye:str, surr:str):
    embed = embed.upper()
    eye = eye.upper()
    surr = surr.upper()
    eyeAdjustment = [[0, -0.5, -2, -2, -2, -2, -2], 
                    [0, 0, -0.5, -2, -2, -2, -2],
                    [0, 0, -0.5, -0.5, -2, -2, -2],
                    [0.5, 0, 0, -0.5, -0.5, -2, -2],
                    [1, 0.5, 0, 0, -0.5, -0.5, -2],
                    [1, 0.5, 0.5, 0, 0, -1, -1],
                    [1, 0.5, 0.5, 0, 0, -0.5, -1]]
    eyeNum = [6.5, 6, 5.5, 5, 4.5, 4.5, 4]

    surrCode = {"CMG":6, "W":5, "B":4, "LG":3, "MG":2, "DG":1, "OW":0, "WMG":0, "CDG":6}
    embedCode = {"CMG":0, "W":1, "B":2, "LG":3, "MG":4, "DG":5, "OW":6, "WMG":6, "CDG":0}
    eyeCode = {"CDG":6, "CMG":6, "W":6, "B":5, "LG":4, "MG":3, "DG":2, "OW":1, "WMG":0}

    flagCheck = 6 - embedCode[embed]
    if(surrCode[surr] < flagCheck or embed == "WMG" or surr == "WMG"):
        await ctx.send("Such combinations are not possible. Did you pass basic arithmetic?")
        return
    await ctx.send("Warning: Eye pattern should only be used if the FT in the previous 12 hours is >= FT2.0!")
    dt = eyeNum[embedCode[embed]] + eyeAdjustment[surrCode[surr]][eyeCode[eye]]
    dt = float(dt)
    await ctx.send(f"DT: {dt}")


@bot.command(name='dvorak_embed')
async def dvorak_embed(ctx, embed:str):
    embed = embed.upper()
    cf = [5, 5, 4.5, 4, 4, 3.5]
    embed_code = {"CDG":0, "CMG":0, "W":0, "B":1, "LG":2, "MG":3, "DG":4, "OW":5, "WMG":5}
    await ctx.send("Warning! Embedded pattern is only allowed if 12 hour FT is >= FT3.5.")
    dt = float(cf[embed_code[embed]])
    await ctx.send(f"DT: {dt}")

@bot.command(name='dvorak_curved')
async def dvorak_curved(ctx, angle:float, col:str):
    col = col.upper()
    colBoost = {"CDG":0.5, "CMG":0.5, "W":0.5, "B":0, "LG":0, "MG":0, "DG":0, "OW":0, "WMG":0}
    dt = 0.0
    if(angle < 0): #Boundary condition
        dt += 1.0
    if(angle <= 0.35):
        dt += 2.0
    elif(angle <= 0.55):
        dt += 2.5
    elif(angle <= 0.75):
        dt += 3.0
    elif(angle <= 1):
        dt += 3.5
    elif(angle <= 1.3):
        dt += 4.0
    elif(angle <= 1.7):
        dt += 4.5
    elif(angle <= 100000):
        dt += 4.5
    else:
        dt += 1.0
    
    dt += colBoost[col]
    await ctx.send(f"DT: {dt}")
    
@bot.command(name='dvorak_shear')
async def dvorak_shear(ctx, dist:float, diam:float):
    if diam <= 1.5:
        await ctx.send("DT: 1.0 to 2.0 (Uncertain)")
        return
    dt = ""
    if dist >= 1.25:
        dt += "Too weak to classify"
    elif dist >= 0.75:
        dt += "DT: 1.0 to 2.0 (Uncertain)"
    elif dist >= 0.5:
        dt += "DT: 2.5"
    elif dist <= 0.49 and dist >= -0.32:
        dt += "DT: 3.0"
    elif(dist < -0.32):
        dt += "DT: 3.5"
    await ctx.send(dt)

@bot.command(name='smapc')
async def smapc(ctx, w10:float):
    #Raw SMAP data as input:
    raw_SMAP = w10

    #Linear regression equation to process the above:
    processed_SMAP = (362.644732816453 * raw_SMAP + 2913.62505913216) / 380.88384339523

    #Display output:
    processed_SMAP = "{:.2f}".format(processed_SMAP)
    await ctx.send(f"Converted 1-min winds: {processed_SMAP} kt")

@bot.command(name='reconfl')
async def reconfl(ctx, winds:float, htOrPres:int):
    converted = 0.0
    flag = ""
    if(htOrPres == 925 or htOrPres == 1500):
        converted += 0.75 * winds
    elif(htOrPres == 850 or htOrPres == 5000):
        converted += 0.80 * winds
    elif(htOrPres == 750):
        converted += 0.87 * winds
    elif(htOrPres == 700 or htOrPres == 10000):
        converted += 0.90 * winds
    elif(htOrPres == 650):
        converted += 0.92 * winds
    elif(htOrPres == 500):
        converted += 0.95 * winds
    else:
        flag += "False"
    
    if flag == "False":
        await ctx.send("Not valid conversions. Allowed values are [925, 850, 750, 700, 650, 500] mb Pressure or [1500, 5000, 10000] ft Height.")
    else:
        converted = "{:.2f}".format(converted)
        await ctx.send(f"The converted FL value = {converted} Kts")

@bot.command(name='mcfetch')
async def mcfetch(ctx, satellite:str, band:str, latitude:float, longitude:float, time:str, day:int, month:int, year:int, mag1="", mag2="", zoom="", eu="", coverage=""):
    if zoom != "" and int(zoom) > 2000:
        await ctx.send("Invalid Zoom parameter!")
        return
    
    if mag1 != "" and mag2 != "" and ((int(mag1) > 0 and int(mag1) < -999) or ((int(mag2) > 0 and int(mag2) < -999))):
        await ctx.send("Out of bounds magnification parameter!")
        return

    import requests
    from io import BytesIO

    if eu != "":
        eu = eu.upper()
    satellite = satellite.upper()
    longitude *= -1
    day = str(day).zfill(2)
    month = str(month).zfill(2)
    await ctx.send("Please be patient as the image loads.")

    if mag1 == "" and mag2 == "" and zoom == "":
        url = f"https://mcfetch.ssec.wisc.edu/cgi-bin/mcfetch?dkey=API_KEY&satellite={satellite}&band={band}&output=JPG&date={year}-{month}-{day}&time={time[:2]}:{time[2:]}&eu={eu}&lat={latitude}+{longitude}&map=YES&size=600+600&mag=-1+-2"
    elif zoom == "":
        url = f"https://mcfetch.ssec.wisc.edu/cgi-bin/mcfetch?dkey=API_KEY&satellite={satellite}&band={band}&output=JPG&date={year}-{month}-{day}&time={time[:2]}:{time[2:]}&eu={eu}&lat={latitude}+{longitude}&map=YES&size=600+600&mag={mag1}+{mag2}"
    else:
        url = f"https://mcfetch.ssec.wisc.edu/cgi-bin/mcfetch?dkey=API_KEY&satellite={satellite}&band={band}&output=JPG&date={year}-{month}-{day}&time={time[:2]}:{time[2:]}&eu={eu}&lat={latitude}+{longitude}&map=YES&size={zoom}+{zoom}&mag={mag1}+{mag2}"
    
    if satellite in ['GOES16', 'GOES17', 'GOES18', 'GOES19', 'HIMAWARI8', 'HIMAWARI9']:
        coverage = coverage.upper()
        url += f"&coverage={coverage}"
    
    response = requests.get(url)
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'mcfetch.jpg'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")
        await ctx.send("For a list of available satellites, go to this link: https://inventory.ssec.wisc.edu/inventory/#calendar")

@bot.command(name='mcfetch_help')
async def mcfetch_help(ctx):
    image2 = 'MCFETCH_Bands.webp'
    image1 = 'documentation.webp'
    with open(image1, 'rb') as image_file:
        image1 = discord.File(image_file)
        await ctx.send(file=image1)
    await ctx.send("Bands available on each satellite under the !mcfetch command:")
    with open(image2, 'rb') as image_file:
        image2 = discord.File(image_file)
        await ctx.send(file=image2)

@bot.command(name='mjo')
async def mjo(ctx, model:str):
    import requests
    from io import BytesIO
    model = model.upper()
    url = ""
        
    if model == 'GFS':
        url += "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/ensplume_full.gif?28183947292"
    elif model == 'ECMWF':
        url += "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/CLIVAR/ECMF.png?28183947292"
    elif model == 'GEFS':
        url += "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/CLIVAR/GEFS.png?28183947292"
    elif model == 'EPS':
        url += "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/CLIVAR/EMON_BC.png?28183947292"
    elif model == 'CFS':
        url += "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/CLIVAR/NCFS.png?28183947292"
    elif model == 'CANM':
        url += "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/CLIVAR/CANM.png?28183947292"
    elif model == 'JMA':
        url += "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/CLIVAR/JMAN.png?28183947292"
    elif model == 'BOM':
        url += "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/CLIVAR/BOMM_BC.png?28183947292"
    else:
        await ctx.send("This model either does not exist, or is not supported.")
        await ctx.send("Supported models: [GFS, GEFS, ECMWF, EPS, CFS, CANM, JMA, BOM]")
        return
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='vp200')
async def vp200(ctx):
    import requests
    from io import BytesIO
    url = "https://www.cpc.ncep.noaa.gov/products/intraseasonal/tlon_vpot_web.gif?28183947292"
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='zonal_anom')
async def zonal_anom(ctx):
    import requests
    from io import BytesIO
    url = "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/MJO/current_anom_850wind.gif?28183947292"
    response = requests.get(url)
    await ctx.send("Please hold as the data loads.")
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)

        await ctx.send(file=discord.File(image_data, 'image.png'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

@bot.command(name='rhoades')
async def rhoades(ctx):
    image_path1 = 'rhoades1.webp'
    image_path2 = 'rhoades2.webp'

    with open(image_path1, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)
    with open(image_path2, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='chappal')
async def chappal(ctx):
    image_path1 = 'chappal.webp'

    with open(image_path1, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='goldstandard')
async def goldstandard(ctx):
    await ctx.send("```IN TERMS OF INTENSITY, "+
"WE HAVE BEEN LUCKY TO RECEIVE TWO GOLD-STANDARD INTENSITY "+
"MEASUREMENTS IN THE LAST THREE HOURS; A 300908Z SMAP PASS REVEALED "+
"118 KNOT 10-MIN WINDS IN THE SOUTHEASTERN QUADRANT, WHICH CONVERT "+
"TO 126 KNOT 1-MIN WINDS, AND A 301001Z RCM-3 PARTIAL SAR PASS. "+
"WHILE THE SAR DID NOT COVER THE ENTIRETY OF THE STORM, IT DID COVER "+
"THE EYE AND THE SOUTHEASTERN QUADRANT, WHERE THE HIGHEST WINDS HAVE "+
"BEEN OVER THE PAST 24 HOURS, AND REVEALED A MAXIMUM WIND OF 129 "+
"KNOTS. THUS THE INTENSITY IS SET TO 130 KNOTS WITH HIGH CONFIDENCE, "+
"REGARDLESS OF THE T7.0 DVORAK BASED ESTIMATES FROM ALL AGENCIES. "+
"130 KNOTS IS ALSO SUPPORTED BY THE ADT, AIDT, DPRINT AND SATCON "+
"ESTIMATES.```")
    
@bot.command(name='susfix')
async def susfix(ctx):
    await ctx.send("```SATELLITE ANALYSIS, INITIAL POSITION AND INTENSITY DISCUSSION:\n"+
"ANIMATED ENHANCED INFRARED (EIR) SATELLITE IMAGERY DEPICTS A COMPACT "+
"YET INTENSE TYPHOON STRENGTH CIRCULATION WITH A LARGE (33NM) EYE. "+
"OVER "+
"THE PAST SEVERAL HOURS, THE ONCE CLOUDY EYE IS NOW MOSTLY CLEAR, "+
"RESULTING IN WARMING EYE TEMPERATURES (10C TO 17C). A 100834Z SSMIS "+
"89GHZ COLOR COMPOSITE MICROWAVE IMAGE REVEALS A ROBUST EYE WALL HAS "+
"FORMED WITH NUMEROUS FEEDER BANDS OF CONVECTION IN ALL QUADRANTS "+
"AROUND IT. A RECENT 101130Z ASCAT-B SCATTEROMETERY PASS INDICATES A "+
"TIGHT AND MOSTLY SYMMETRIC WIND FIELD, SLIGHTLY FAVORING THE "+
"NORTHEASTERN QUADRANT. THE INITIAL POSITION IS PLACED WITH HIGH "+
"CONFIDENCE BASED ON EIR, SSMIS AND SCATTEROMETERY DATA. THE INITIAL "+
"INTENSITY OF 75 KTS IS ASSESSED WITH MEDIUM CONFIDENCE BASED ON "+
"AGENCY "+
"DVORAK INTENSITY ESTIMATES WHICH MOSTLY SUPPORT 75KTS, WHILE THE BULK "+
"OF THE REMAINING AUTOMATED INTENSITY ESTIMATES ARE SUSPICIOUSLY HIGH, "+
"IN MOST CASES HOVERING NORTH OF 100KTS.```")

@bot.command(name='bualoiFix')
async def bualoiFix(ctx):
    result = ""
    await ctx.send("```TPPN11 PGTW 220943"+
"\nA. TROPICAL STORM 22W (BUALOI)"+
"\nB. 21/0900Z"+
"\nC. 18.61N"+
"\nD. 143.93E"+
"\nE. ONE/HMWRI8"+
"\nF. T6.5/6.5/D1.0/24HRS STT: D1.0/03HRS"+
"\nG. IR/EIR"+
"\nH. REMARKS: 01A/PBO EYE/ANMTN. WMG EYE SURROUNDED BY W YIELDS"+
"\nAN E# OF 6.0. ADDED 1.0 EYE ADJUSTMENT FOR W, TO YIELD A DT OF"+
"\n7.0. MET AND PT YIELD A 6.5. DBO PT."+
"\nI. ADDITIONAL POSITIONS:"+
"\n22/0404Z 17.80N 144.68E ATMS"+
"\nRICHARDSON```")

@bot.command(name='cccfix')
async def cccfix(ctx):
    import requests
    await ctx.send("```TPPN10 PGTW 151514"+
"\nA. TYPHOON 28W (RAI)"+
"\nB. 15/1430Z"+
"\nC. 9.66N"+
"\nD. 129.22E"+
"\nE. FIVE/HMWRI8"+
"\nF. T4.0/4.0/S0.0/24HRS STT: S0.0/03HRS"+
"\nG. IR/EIR "+
"\nH. REMARKS: 38A/PBO . COLD CENTRAL COVER YIELDS DT OF 4.0. MET & PT AGREE. DBO DT."+
"\nI. ADDITIONAL POSITIONS: NONE"+
"\nAMARAL```")
    
    image_path = 'ccc.webp'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='wpacmenu')
async def wpacmenu(ctx):
    await ctx.send("```Menu:"+
"\n\nStarter:"+
"\nMawar/Kulap Sauce w/ Bread"+

"\n\nSoup:"+
"\nMeranti Yinxing Soup with Ampil Garnish"+

"\n\nMain:"+
"\nMegi braised in soy sauce"+
"\nSteamed Jelawat"+
"\nFried Sepat"+
"\nKajiki Sashimi"+
"\nCooked Tapah with Guchol seasoning"
"\nNeoguri Instant Noodles"+

"\n\nDessert:"+
"\nBebinca"+
"\nBualoi"+
"\nKhanun/Nangka"+
"\nPulasan"+
"\nKrathon"+
"\nHigos"+

"\n\nDrink:"+
"\nYun-Yeung"+
"\nMilktea```")

@bot.command(name='tolkienhatesnatl')
async def tolkienhatesnatl(ctx):
    await ctx.send("```But I say to thee, Bustlantic Weenies, I will not be thy tool! I am Steward of the House of Haibus." +
                    "I will not step down to be the dotard chamberlain of an upstart. Even were Lee's claim proved to me, "+
                    "still he comes but of the line of Lorenzo. I will not bow to such a one, last of a ragged basin long "+
                    "bereft of organisation and cloud tops. I would have things as they were in all the days of my life, " +
                    "and in the days of my longfathers before me: to be the lord of the TCs in peace, and leave my chair "+
                    "to a son after me, who would be his own master and not the dry air's pupil. But if doom denies "+
                    "this to me, then I will have naught: neither life diminished, nor love halved, nor honour abated. "+ 
                    "So! Thou hadst already stolen half my loved wejjes. Now thou stealest the MJO and SSTs also, "+
                    "so that they rob me wholly of my wejjes at last. But in this at least thou shalt not defy my will: "+
                    "to rule my own end.```")

@bot.command(name='bestestAgency')
async def bestestAgency(ctx):
    await ctx.send("```Major breakthrough came during cyclone Phalin which hit Odisha coast on 12th October, 2013 near Gopalpur."+
                   " Entire world went wrong and India proved right, when the Extremely Severe Cyclonic Storm, Phailin hit the "+
                   "Odisha coast on 12th October, 2013. India wrought the history. It was monitored and predicted under the "+
                   "leadership of Dr. M. Mohapatra, Director Cyclone warning Division."+
                   " Entire World appreciated IMD and IMD emerged as a global leader in tropical cyclones monitoring and forecasting.```")
    image_path = 'TrulyTheBestAgency.PNG'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='death')
async def death(ctx):
    image_path = 'chris.gif'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)


@bot.command(name='roastepac')
async def roastepac(ctx):
    image_path = 'epactrash3.png'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='roastnatl')
async def roastnatl(ctx):
    image_path = 'Slop_Cereal.png'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='roastspac')
async def roastspac(ctx):
    image_path = 'spac.gif'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='roastwpac')
async def roastwpac(ctx):
    image_path = 'luke.webp'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='gati')
async def gati(ctx):
    image_path = 'Gati.PNG'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='kohli')
async def kohli(ctx):
    image_path = 'king-kohli-haris-rauf.mp4'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='erick')
async def erick(ctx):
    image_path = 'Erick.PNG'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='bustymodelcane')
async def bustymodelcane(ctx):
    image_path = 'modelcane.PNG'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='obama')
async def obama(ctx):
    image_path = 'Obama.PNG'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='linda')
async def obama(ctx):
    image_path = 'linda.PNG'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='pasch')
async def obama(ctx):
    image_path = 'pasch.PNG'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)


@bot.command(name='mjv')
async def obama(ctx):
    image_path = 'mjv.PNG'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='iceberg')
async def iceberg(ctx):
    await ctx.send("https://icebergcharts.com/i/Cyclones")

@bot.command(name='commandHelp')
async def commandHelp(ctx):
    result = ""
    result += "The most commonly used commands for the bot: "
    result += "```\n1. !ckz [Winds, Storm Movement, Latitude, ROCI, ENVP] to calculate the output of the CKZ W/P relationship."
    result += "\n\n2. !rev_ckz [Pressure, Storm Movement, Latitude, ROCI, ENVP] to calculate the output of the reverse of the CKZ W/P relationship."
    result += "\n\n3. !ah77 [Winds] to get the output of the AH77 " 
    result += "\n\n4. !tcsst [Best Track ID, Year] as seen in NOAA SSD Archives."
    result += "\n\n5. !ibtracs [Best Track ID or Name of storm, Year]"
    result += "\n\n6. !jordan [Height at 700mb in metres]"
    result += "\n\n7. !hursat [Best Track ID or Name of storm, Year] to generate the HURSAT link."
    result += "\n\n8. !shear [westpac, eastpac, seastpac, atlantic, europe, indian, austwest, austeast] to generate the CIMSS shear plots."
    result += "\n\n9. !dvorak_eye [Embedded, Eye, Surround] to get the DT value for eye scene in the Dvorak Technique."
    result += "\n\n10. !mjo [Model] To find MJO predictions. GFS and ECMWF supported."
    result += "\n\n11. !atcf Displays the current atcf file as well as decoded information."
    result += "\n\n12. !btk [Best Track ID, Year] as seen in NOAA SSD Archives; returns relevant info from the latest BT."
    result += "\n\n13. !vort [Basin, Pressure in mb/hPa]. Allowed values are [200, 500, 700, 850, 925] mb/hPa for relative vorticity."
    result += "\n\n14. !ersst [Month, Year] to generate the ERSST v5 Values for the month and year."
    result += "\n\n15. !smap [Storm ID, Node] Plot the SMAP data today for the storm ID on the ATCF and specify as either Ascending (asc) or Descending (desc) to get the values."
    result += "\n\n16. !season [Basin, Year] to generate the Seasonal summary map for those year and basins, with ACE."
    result += "\n\n17. !gibbs [Satellite, Scene Type, Hour, Day, Month, Year] to generate the full disk images based on these parameters.```"
    
    url = "https://docs.google.com/document/d/13cuL5KGraO8JRG8oZHoUTIdd01doIJvwn88pSuJNODI/edit?usp=sharing"
    await ctx.send(result)
    await ctx.send("For the full command list, consult the google document here:\n")
    await ctx.send(url)

bot.run(AUTHENTICATION_TOKEN)

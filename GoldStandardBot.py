import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
intents.dm_messages = True
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
    atcf_url = 'https://science.nrlmry.navy.mil/geoips/tcdat/sectors/atcf_sector_file'

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
        await ctx.send(f"```No storms are active. If you believe this is an error, use !atcfv2 as the backup command.```")
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

@bot.command(name='atcfv2', help='Display ATCF storm data from API')
async def atcfv2(ctx, info=""):
    import urllib3
    import json

    # Step 1: Fetch ATCF data from the new API
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')

    atcf_api_url = 'https://api.knackwx.com/atcf/v2'

    def fetch_atcf_data(url):
        try:
            response = http.request('GET', url)
            return json.loads(response.data.decode('utf-8'))
        except Exception as e:
            return None

    # Step 2: Display storm data
    def display_storm_info(storm_data):
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

        def designation(basin, winds):
            winds = int(winds)
            if winds >= 130 and basin == 'W':
                return "Super Typhoon"
            elif winds >= 100:
                return "Major Hurricane" if basin in ['L', 'E', 'C'] else "Major Typhoon"
            elif winds >= 65:
                return "Hurricane" if basin in ['L', 'E', 'C'] else "Typhoon"
            elif winds >= 50 and basin in ['W', 'S']:
                return "Severe Tropical Storm"
            elif winds >= 35:
                return "Tropical Storm"
            elif winds >= 25:
                return "Tropical Depression (Autoflagged)"
            else:
                return "Tropical Low"

        result = ""
        
        result = "\nDecoded storm information from the ATCF API:\n"
        flag = 0
        for storm in storm_data:
            if len(info) > 0:
                basin_code = storm['atcf_id'][-1]
                storm_status = designation(basin_code, storm['winds'])
                result += (f"\n```Storm ID: {storm['atcf_id']}\n"
                        f"Name: {storm_status} {storm['storm_name']}\n"
                        f"Date of Reading: {storm['analysis_time'][:10]}\n"
                        f"Time of Reading: {storm['analysis_time'][11:16]} UTC\n"
                        f"Coordinates: {storm['latitude']}N, {storm['longitude']}E\n"
                        f"Basin: {basin_list.get(basin_code, 'Unknown Basin')}\n"
                        f"Intensity: {storm['winds']} Kts / {storm['pressure']} hPa\n"
                        f"Storm Nature: {storm['cyclone_nature']}```")
            else:
                flag = 1
                result += f"{storm['atcf_sector_file']}\n"
        if flag:
            result = "```" + result + "```"
        result += "Powered by Knack's ATCF v2 API"
        return result

    # Step 3: Fetch and handle API data
    storm_data = fetch_atcf_data(atcf_api_url)
    
    if not storm_data or len(storm_data) == 0:
        await ctx.send("```No storms are active.```")
        return
    
    # Step 4: Display the storm information
    storm_info = display_storm_info(storm_data)
    await ctx.send(storm_info)

@bot.command(name='btk', help='Get data on the most recent storms')
async def btk(ctx, btkID:str, yr:str, plotter=''):
    import urllib3
    from bs4 import BeautifulSoup
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.lines import Line2D
    import os
    import numpy as np
    import matplotlib.colors as mcolors
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    #http = urllib3.PoolManager(cert_reqs='CERT_NONE')

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    btkID = btkID.lower()

    def _00x_to_xx00(des):
        convert_map = {"l": "al", "e": "ep", "c": "cp", "w":"wp", "a":"io", "b":"io", "s":"sh", "p":"sh"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[a-z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    if btkID[:2] in ['sh', 'wp', 'io']:
        btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{yr}.dat'
    else:
        btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{yr}.dat'
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
                if(int(params[2][-2:]) % 6 == 0 and params[11].strip() == '34' and params[10].strip() not in ['DB', 'EX', 'LO', 'WV', 'MD', 'TD', 'SD']):
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

    if len(plotter) > 0:
        await ctx.send("Plotting BT data:")
        idl = False

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

                if(float(cdx[-1]) < -178 or float(cdx[-1]) > 178):
                    idl = True

                winds.append(int(parameters[8].strip()))
                status.append(parameters[10].strip())
                timeCheck.append((parameters[2][-2:].strip()))
                date = parameters[2].strip()
                date = f'{date[:4]}-{date[4:6]}-{date[6:8]} {timeCheck[-1]}:00:00'
                DateTime.append(date)
                pres.append(int(parameters[9].strip()))
                r34.append(int(parameters[11].strip()))
                stormName = parameters[27].strip()

        #Beginning work on the actual plotting of the data:
        if idl == True:
            fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
        else:
            fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

        from matplotlib import colors
    
        ax.add_feature(cfeature.COASTLINE, linewidth=1, color="c")
        ax.add_feature(cfeature.BORDERS, color="w", linewidth=0.5)
        ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
        if idl == False:
            ax.add_feature(cfeature.OCEAN, facecolor='#191919')

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
        '''
        if ratio < 0.3: 
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
        elif ratio > 0.7:
            ax.set_xlim(center_x-(center_height), center_x+(center_height))
            ax.set_ylim(center_y-center_height, center_y+center_height)
        else:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-center_height, center_y+center_height)
        '''
        #----NEW-----
        ax.set_xlim(minLong-2, maxLong+2)
        ax.set_ylim(minLat-2, maxLat+2)
        #------------

        #Defining the legend box for the plot...
        legend_elements = [
                        Line2D([0], [0], marker='^', color='w', label='Non-Tropical',markerfacecolor='#444764', markersize=10),
                        Line2D([0], [0], marker='s', color='w', label='Sub-Tropical',markerfacecolor='#444764', markersize=10),
                        #Line2D([0], [0], marker='o', color='w', label='Tropical Depression',markerfacecolor='b', markersize=10),
                        #Line2D([0], [0], marker='o', color='w', label='Tropical Storm',markerfacecolor='g', markersize=10),
                        #Line2D([0], [0], marker='o', color='w', label='Category 1',markerfacecolor='#ffff00', markersize=10),
                        #Line2D([0], [0], marker='o', color='w', label='Category 2',markerfacecolor='#ffa001', markersize=10),
                        #Line2D([0], [0], marker='o', color='w', label='Category 3',markerfacecolor='#ff5908', markersize=10),
                        #Line2D([0], [0], marker='o', color='w', label='Category 4',markerfacecolor='r', markersize=10),
                        #Line2D([0], [0], marker='o', color='w', label='Category 5',markerfacecolor='m', markersize=10),
        ]

        # Define the color mapping for wind speeds
        colors = ['b', 'g', '#ffff00', '#ffa001', '#ff5908', 'r', 'm']
        bounds = [0, 34, 64, 81, 96, 112, 137, 200]
        norm = mcolors.BoundaryNorm(bounds, len(colors))
        labels = ['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5']

        #Building the function that calculates ACE...
        def calc_ACE(winds, timeCheck):
            ace = 0
            aceList = []
            for i in range(len(winds)):
                if(winds[i] == ' '):
                    continue
                time = int(timeCheck[i]) % 6 #If it is synoptic time and meets...
                if(time==0 and r34[i] == 34 and int(winds[i]) >= 34 and status[i] not in ['DB', 'LO', 'WV', 'EX']): 
                    ace += (int(winds[i]) ** 2) / 10000
                aceList.append(ace)
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
        plt.plot(LineX, LineY, color="#808080", linestyle="-")

        #Applying final touches...
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title(f'{btkID.upper()}{yr} {stormName}')
        plt.title(f'VMAX: {vmax} Kts', loc='left', fontsize=9)
        plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right', fontsize=9)
        ax.legend(handles=legend_elements, loc='upper right')
        plt.grid(True)

        #-----NEW-----------
        # Create the colorbar
        cmap = mcolors.ListedColormap(colors)
        norm = mcolors.BoundaryNorm(bounds, cmap.N)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        ax.legend(handles=legend_elements, loc='best')

        # Add colorbar to the plot
        cbar = plt.colorbar(sm, ticks=bounds, orientation='horizontal', pad=0.05, aspect=50, ax=ax, shrink=0.5)
        cbar.set_label('SSHWS Windspeeds (Kts)')
        cbar.ax.set_xticklabels(['0', '34', '64', '81', '96', '112', '137', '200'])
        #---------------------
        plt.tight_layout()
        
        r = np.random.randint(1, 10)
        image_path = f'Track_Map{r}.png'
        plt.savefig(image_path, format='png', bbox_inches='tight')
        plt.close()

        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

        os.remove(image_path)  

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
    if header[-1] == 'S' or header[-1] == 'P':
        from datetime import datetime
        basinDate = datetime.now()
        basinmonth = basinDate.month
        basinYear = basinDate.year
        if basinmonth >= 7:
            btkUrl = f'https://tropic.ssec.wisc.edu/real-time/amsu/archive/{basinYear+1}/{basinYear+1}{header}/intensity.txt'
        else:
            btkUrl = f'https://tropic.ssec.wisc.edu/real-time/amsu/archive/{basinYear}/{basinYear}{header}/intensity.txt'
    else:
        btkUrl = f'https://tropic.ssec.wisc.edu/real-time/amsu/archive/{basinYear}/{basinYear}{header}/intensity.txt'

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
    def final_roci(roci):
        return max((roci / 60) / 8 + 0.1, 0.4)  # if ROCI < 0.4, default to 0.4

    def final_move(movespeed):
        return 1.5 * math.pow(movespeed, 0.63)

    def calculate_wind(pressure, movespeed, lat, roci, envpres):
        a = 1 / (18.26 ** 2) if lat <= 18 else 1 / (24.254 ** 2)
        b = 0.267 if lat <= 18 else 0.483
        c = (pressure - 5.962 - envpres - 2 + (6.8 * final_roci(roci))) if lat <= 18 \
            else (pressure - 23.286 - envpres - 2 + (12.587 * final_roci(roci)) + (0.483 * lat))
        
        discriminant = b ** 2 - 4 * a * c  # b^2 - 4ac
        
        if discriminant < 0:
            return "No real solution"
        
        wind1 = (-b + math.sqrt(discriminant)) / (2 * a) + final_move(movespeed)
        wind2 = (-b - math.sqrt(discriminant)) / (2 * a) + final_move(movespeed)
        
        positive_wind = next((wind for wind in [wind1, wind2] if wind >= 0), None)
        
        return f":arrow_forward: {positive_wind:.2f} knots" if positive_wind is not None else "No valid wind speed"
    
    await ctx.send(calculate_wind(pres, storm_movement, latitude, roci, envp))
    #Legacy Code below
    '''
    latitude = abs(latitude)
    poci = pres - 6 #Approximation to reduce the error

    #S-ratio calculation...
    S = (roci/60)/8 + 0.1
    if(S < 0.4):
        S = 0.4

    delP = abs(poci - envp)

    #Implementing reverse CKZ equation from KZ et al. 2007:
    vmax = 18.633 - 14.690 * S - 0.755 * latitude - 0.518 * (poci - envp) + 9.378 * math.sqrt(delP) + 1.5 * storm_movement ** 0.63

    #Make the output a little presentable:
    vmax = "{:.2f}".format(vmax)
    await ctx.send(f"Output winds: {vmax} kt")'''

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
    url = f"https://www.star.nesdis.noaa.gov/pub/socd/mecb/crw/data/5km/v3.1_op/image_browse/daily/ssta/png/{year}/ct5km_ssta_v3.1_global_{year}{month_f}{day_f}.png"
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

@bot.command(name='mw')
async def mw(ctx, btkID:str, mw_type:str, lookback=1):
    mw_type = mw_type.lower()
    btkID = btkID.lower()
    if mw_type not in ['low', 'mid', 'upper', 'lower', 'up']:
        await ctx.send("Invalid MW type. Please send operational storm data in these three types: ['Low', 'Mid', 'Upper']")
        return None
    import json
    import urllib3
    from io import BytesIO

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    url = ""
    if mw_type == 'mid':
        url = f"https://science.nrlmry.navy.mil/geoips/prod_api/tcweb/products/{btkID[4:]}?storm_id={btkID}&product=89H&product=91H"
    if mw_type == 'low' or mw_type == 'lower':
        url = f"https://science.nrlmry.navy.mil/geoips/prod_api/tcweb/products/{btkID[4:]}?storm_id={btkID}&product=color34&product=color37"
    if mw_type == 'up' or mw_type == 'upper':
        url = f"https://science.nrlmry.navy.mil/geoips/prod_api/tcweb/products/{btkID[4:]}?storm_id={btkID}&product=165H&product=176H&product=180H&product=182H&product=183-1H&product=183-3H&product=183H&product=18p7H-aft&product=184p4&product=204p8&product=TB325-1"

    # Make the request
    response = http.request('GET', url)

    # Print raw response data for debugging
    response_data = response.data.decode('utf-8')
    #print(f"Raw response data:", response_data)

    # Check the content type
    if response.headers.get('Content-Type') == 'application/json':
        try:
            # Parse the JSON response
            data = json.loads(response_data)
            #print(f"Parsed data", data)
            #print(data.get('data', [])) 
        except json.JSONDecodeError as e:
            print(f"JSON decode error:", e)
    else:
        print(f"Unexpected content type for:", response.headers.get('Content-Type'))

    from datetime import datetime

    products_sorted = sorted(
        data.get('products', []),
        key=lambda x: datetime.fromisoformat(x['product_date']),
        reverse=True  # Most recent first
    )

    if lookback < 1:
        await ctx.send("Invalid lookback value. You can't see the future!")
        return None

    if len(products_sorted) >= lookback:
        selected = products_sorted[lookback - 1]
        if lookback > 1:
            await ctx.send(f"Latest available product on lookback = {lookback}: {selected['product']} from {selected['sensor']} on {selected['product_date']}")
        else:
            await ctx.send(f"Latest available product: {selected['product']} from {selected['sensor']} on {selected['product_date']}")
        image_url = selected['product_url'].replace("http://", "https://")
    else:
        await ctx.send(f"Not enough products to look back {lookback} steps.")
        return None

    # Fetch the image
    img_response = http.request('GET', image_url)
    img_bytes = BytesIO(img_response.data)
    img_bytes.seek(0)
    await ctx.send(file=discord.File(img_bytes, 'image.png'))

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

@bot.command(name='tcpass_custom')
async def tcpass_custom(ctx, latitude:float, longitude:float, width=4):
    import urllib3
    from bs4 import BeautifulSoup
    import json
    from datetime import datetime, timedelta
    from urllib.parse import quote
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import matplotlib.cm as cm
    import math
    import os
    import numpy as np
    
    await ctx.send("Please wait. Due to API service times, the figure may take a few seconds to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    # Define the bounding box around the point
    box_size = 2*width  # Bounding box size in degrees
    upper_right = f"{latitude + box_size},{longitude + box_size}"
    lower_left = f"{latitude - box_size},{longitude - box_size}"

    # Get the current UTC time
    now = datetime.utcnow()
    start_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Calculate the end time (6 hours from now)
    end_time = (now + timedelta(hours=6)).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Initialize the HTTP client
    http = urllib3.PoolManager()

    SATELLITES = ["29522", "35951", "28054", "27424", "25994", "39260", "43010", "41882",
                "38337", "38771", "43689", "54234", "43013", "33591", "28654", "37849",
                "39574", "39634", "36036", "40376", 
                "44322", "44324", "44323", "32382", "64694", "59481", "62261"]
    #Archived TROPICS Passes: "56753", "56442", "56444", "56754", 
    satelliteMap = {"28054":"DMSP F16", "29522":"DMSP F17", "35951":"DMSP F18", "27424":"AQUA",
                    "25994": "TERRA", "39260":"FENGYUN 3C", "43010":"FENGYUN 3D", "41882":"FENGYUN 4A",
                    "38337":"GCOM-W1", "38771":"METOP-B", "43689":"METOP-C", "54234":"NOAA 21", "43013":"NOAA 20",
                    "33591":"NOAA 19", "28654":"NOAA 18", "37849":"SUOMI NPP", "39574":"GPM-CORE", 
                    "56753":"TROPICS-03", "56442":"TROPICS-05", "56444":"TROPICS-06", "56754":"TROPICS-07", "39634":"SENTINEL-1A",
                    "36036": "SMOS", "40376":"SMAP", "44322":"RCM-1", "44324":"RCM-2", "44323":"RCM-3", "32382":"RADARSAT-2",
                    "64694":"GOSAT-GW", "59481":"WSF-M", "62261":"SENTINEL-1C"}


    # Function to fetch data for a single satellite
    def fetch_data_for_satellite(satellite):
        url = (
            f"http://sips.ssec.wisc.edu/orbnav/api/v1/overpass.json?"
            f"sat={quote(satellite)}"
            f"&start={quote(start_time)}&end={quote(end_time)}"
            f"&ur={quote(upper_right)}&ll={quote(lower_left)}"
        )
        
        # Make the request
        response = http.request('GET', url)
        
        # Print raw response data for debugging
        response_data = response.data.decode('utf-8')
        #print(f"Raw response data for {satellite}:", response_data)
        
        # Check the content type
        if response.headers.get('Content-Type') == 'application/json':
            try:
                # Parse the JSON response
                data = json.loads(response_data)
                #print(f"Parsed data for {satellite}:", data)
                return data.get('data', [])  # Return the parsed data list
            except json.JSONDecodeError as e:
                print(f"JSON decode error for {satellite}:", e)
                return None
        else:
            print(f"Unexpected content type for {satellite}:", response.headers.get('Content-Type'))
            return None
        
        # Function to calculate distance between two coordinates
    def haversine(lat1, lon1, lat2, lon2):
        radius = 6378.137  # Radius of the Earth in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius * c
    from matplotlib import colors
    # List to hold all overpass points
    fig = plt.figure(figsize=(10, 5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, linewidth=1, color="c")
    ax.add_feature(cfeature.BORDERS, color="w", linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))

    # Use a colormap to get distinct colors
    colors = cm.tab20b.colors + cm.tab20c.colors

    await ctx.send("Data recieved, plotting points...")
    for idx, satellite in enumerate(SATELLITES):
        data = fetch_data_for_satellite(satellite)
        if data:
            color = colors[idx % len(colors)]  # Get a color from the colormap
            lats, lons = [], []
            min_distance = float('inf')
            min_distance_point = None
            min_distance_date = None
            plotted_points = []
            
            for point in data:
                try:
                    lat, lon = float(point[2]), float(point[3])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        distance = haversine(latitude, longitude, lat, lon)
                        if distance <= (width*100) and distance < min_distance:
                            min_distance = distance
                            min_distance_point = (lat, lon)
                            min_distance_date = datetime.strptime(point[0], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m\n%H:%M UTC')
                        
                        lats.append(lat)
                        lons.append(lon)
                        plotted_points.append(ax.plot(lon, lat, 'o',color=color, markersize=0.01))
                except ValueError as e:
                    print(f"ValueError for point {point}: {e}")
            
            if lats and lons:
                min_distance = "{:.2f}".format(min_distance)
                label_text = f"{satelliteMap.get(satellite, satellite)}\n{min_distance_date}\n{min_distance} km"
                plotted_path = ax.plot(lons, lats, color=color, linewidth=1, linestyle='-', alpha=1, label=label_text)
            
            if min_distance_point:
                min_lat, min_lon = min_distance_point
                ax.plot(min_lon, min_lat, 'x', color='r', markersize=5)
                #min_distance = "{:.2f}".format(min_distance)
                #ax.text(min_lon, min_lat, min_distance_date+f"\n{min_distance} km", fontsize=8, color='red', ha='right')
            else:
                # Remove plotted points if min_distance_point is not found
                for plot in plotted_points:
                    plot.pop().remove()
                # Remove plotted path if min_distance_point is not found
                if 'plotted_path' in locals():
                    plotted_path.pop(0).remove()
    
    ax.plot(longitude, latitude, 'x', color='c', markersize=5)

    # Set map extent to show the area of interest
    ax.set_extent([longitude - width, longitude + width, latitude - width, latitude + width])
    gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gls.top_labels = False   # suppress top labels
    gls.right_labels = False  # suppress right labels

    plt.title(f"Expected pass times for ({latitude}, {longitude})\n (< {width*100}km from Center)")
    plt.legend(
    loc='upper center',            # Place the legend at the top center of the bounding box
    bbox_to_anchor=(0.5, -0.15),   # Adjust the legend to be at the bottom of the box
    fontsize='small',              # Set the font size
    ncol=len(SATELLITES),          # Display the legend items in a single horizontal row
    title='Satellites'             # Set the title of the legend
    )

    r = np.random.randint(1, 10)
    image_path = f'TC_PASS{r}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)   

@bot.command(name='tcpass')
async def tcpass(ctx, btkID: str):
    import urllib3
    from bs4 import BeautifulSoup
    import json
    import urllib3
    from datetime import datetime, timedelta
    from urllib.parse import quote
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import matplotlib.cm as cm
    import math
    import os
    import numpy as np
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
    btkID = btkID.lower()
    def _00x_to_xx00(des):
        convert_map = {"l": "al", "e": "ep", "c": "cp", "w":"wp", "a":"io", "b":"io", "s":"sh", "p":"sh"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[a-z]$", btkID):    
        btkID = _00x_to_xx00(btkID)
    await ctx.send("Please wait. Due to API service times, the figure may take a few seconds to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    #http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()
    
    from datetime import datetime
    basinDate = datetime.now()
    basinmonth = basinDate.month
    basinYear = basinDate.year
    if btkID[:2] in ['sh', 'wp', 'io']:
        if btkID[:2] == 'sh':
            if basinmonth >= 7:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear+1}.dat'
            else:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
        else:
            btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
    else:
        btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'

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
    
    # Define the geographic point
    latitude = centerY
    longitude = centerX

    # Define the bounding box around the point
    box_size = 14  # Bounding box size in degrees
    upper_right = f"{latitude + box_size},{longitude + box_size}"
    lower_left = f"{latitude - box_size},{longitude - box_size}"

    # Get the current UTC time
    now = datetime.utcnow()
    start_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Calculate the end time (6 hours from now)
    end_time = (now + timedelta(hours=6)).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Initialize the HTTP client
    http = urllib3.PoolManager()

    SATELLITES = ["29522", "35951", "28054", "27424", "25994", "39260", "43010", "41882",
                "38337", "38771", "43689", "54234", "43013", "33591", "28654", "37849",
                "39574", "39634", "36036", "40376", 
                "44322", "44324", "44323", "32382", "64694", "59481", "62261"]
    #Archived TROPICS Passes: "56753", "56442", "56444", "56754", 
    satelliteMap = {"28054":"DMSP F16", "29522":"DMSP F17", "35951":"DMSP F18", "27424":"AQUA",
                    "25994": "TERRA", "39260":"FENGYUN 3C", "43010":"FENGYUN 3D", "41882":"FENGYUN 4A",
                    "38337":"GCOM-W1", "38771":"METOP-B", "43689":"METOP-C", "54234":"NOAA 21", "43013":"NOAA 20",
                    "33591":"NOAA 19", "28654":"NOAA 18", "37849":"SUOMI NPP", "39574":"GPM-CORE", 
                    "56753":"TROPICS-03", "56442":"TROPICS-05", "56444":"TROPICS-06", "56754":"TROPICS-07", "39634":"SENTINEL-1A",
                    "36036":"SMOS", "40376":"SMAP", "44322":"RCM-1", "44324":"RCM-2", "44323":"RCM-3", "32382":"RADARSAT-2",
                    "64694":"GOSAT-GW", "59481": "WSF-M", "62261":"SENTINEL-1C"}


    # Function to fetch data for a single satellite
    def fetch_data_for_satellite(satellite):
        url = (
            f"http://sips.ssec.wisc.edu/orbnav/api/v1/overpass.json?"
            f"sat={quote(satellite)}"
            f"&start={quote(start_time)}&end={quote(end_time)}"
            f"&ur={quote(upper_right)}&ll={quote(lower_left)}"
        )
        
        # Make the request
        response = http.request('GET', url)
        
        # Print raw response data for debugging
        response_data = response.data.decode('utf-8')
        #print(f"Raw response data for {satellite}:", response_data)
        
        # Check the content type
        if response.headers.get('Content-Type') == 'application/json':
            try:
                # Parse the JSON response
                data = json.loads(response_data)
                #print(f"Parsed data for {satellite}:", data)
                return data.get('data', [])  # Return the parsed data list
            except json.JSONDecodeError as e:
                print(f"JSON decode error for {satellite}:", e)
                return None
        else:
            print(f"Unexpected content type for {satellite}:", response.headers.get('Content-Type'))
            return None
        
        # Function to calculate distance between two coordinates
    def haversine(lat1, lon1, lat2, lon2):
        radius = 6378.137  # Radius of the Earth in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius * c
    
    from matplotlib import colors
    # List to hold all overpass points
    fig = plt.figure(figsize=(10, 5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, linewidth=1, color="c")
    ax.add_feature(cfeature.BORDERS, color="w", linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))

    # Use a colormap to get distinct colors
    colors = cm.tab20b.colors + cm.tab20c.colors

    await ctx.send("Data recieved, plotting points...")
    for idx, satellite in enumerate(SATELLITES):
        data = fetch_data_for_satellite(satellite)
        if data:
            color = colors[idx % len(colors)]  # Get a color from the colormap
            lats, lons = [], []
            min_distance = float('inf')
            min_distance_point = None
            min_distance_date = None
            plotted_points = []
            
            for point in data:
                try:
                    lat, lon = float(point[2]), float(point[3])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        distance = haversine(latitude, longitude, lat, lon)
                        if distance <= 700 and distance < min_distance:
                            min_distance = distance
                            min_distance_point = (lat, lon)
                            min_distance_date = datetime.strptime(point[0], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m\n%H:%M UTC')
                        
                        lats.append(lat)
                        lons.append(lon)
                        plotted_points.append(ax.plot(lon, lat, 'o',color=color, markersize=0.01))
                except ValueError as e:
                    print(f"ValueError for point {point}: {e}")
            
            if lats and lons:
                min_distance = "{:.2f}".format(min_distance)
                label_text = f"{satelliteMap.get(satellite, satellite)}\n{min_distance_date}\n{min_distance} km"
                plotted_path = ax.plot(lons, lats, color=color, linewidth=1, linestyle='-', alpha=1, label=label_text)
            
            if min_distance_point:
                min_lat, min_lon = min_distance_point
                ax.plot(min_lon, min_lat, 'x', color='r', markersize=5)
                #min_distance = "{:.2f}".format(min_distance)
                #ax.text(min_lon, min_lat, min_distance_date+f"\n{min_distance} km", fontsize=8, color='red', ha='right')
            else:
                # Remove plotted points if min_distance_point is not found
                for plot in plotted_points:
                    plot.pop().remove()
                # Remove plotted path if min_distance_point is not found
                if 'plotted_path' in locals():
                    plotted_path.pop(0).remove()
    
    ax.plot(longitude, latitude, 'x', color='c', markersize=5)

    # Set map extent to show the area of interest
    ax.set_extent([longitude - 7, longitude + 7, latitude - 7, latitude + 7])
    gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gls.top_labels = False   # suppress top labels
    gls.right_labels = False  # suppress right labels

    plt.title(f"Expected pass times for {btkID.upper()} {stormName} (< 700km from Center)")
    plt.legend(
    loc='upper center',            # Place the legend at the top center of the bounding box
    bbox_to_anchor=(0.5, -0.15),   # Adjust the legend to be at the bottom of the box
    fontsize='small',              # Set the font size
    ncol=len(SATELLITES),          # Display the legend items in a single horizontal row
    title='Satellites'             # Set the title of the legend
    )
    r = np.random.randint(1, 10)
    image_path = f'TC_PASS{r}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)  

@bot.command(name='uwind_anomaly')
async def uwind_anomaly(ctx, hour:str, date:str, pressure_level=850):
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import matplotlib.style as mplstyle
    import matplotlib.colors as mcolors
    import requests
    import os
    mplstyle.use("dark_background")

    day, month, year = str(date).split('/')[0], str(date).split('/')[1], str(date).split('/')[2]
    download_url = f'https://psl.noaa.gov/cgi-bin/mddb2/plot.pl?doplot=0&varID=158978&fileID=0&itype=0&variable=uwnd&levelType=Pressure%20Levels&level_units=millibar&level={pressure_level}.0&timetype=4x&fileTimetype=4x&year1={year}&month1={month}&day1={day}&hr1={hour.zfill(2)}%20Z&year2={year}&month2={month}&day2={day}&hr2={hour.zfill(2)}%20Z&region=Custom&area_north=20&area_west=0&area_east=360&area_south=-20&centerLat=0.0&centerLon=270.0'
    filename = 'Test_ncep_uwind_anomaly.nc'
    await ctx.send("Downloading relevant data...")
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Check for HTTP errors

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Data successfully downloaded to {filename}")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"An error occurred while downloading the data: {e}")
        return
    await ctx.send("Data downloaded, plotting...")
    ds = xr.open_dataset(filename)

    zonal_mean = ds.uwnd.mean(dim='lon')
    lon, lat = ds.lon, ds.lat
    uwind_anomaly = ds.uwnd - zonal_mean
    uwind_anomaly_2d = uwind_anomaly.squeeze()

    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(20, 20))

    ax.add_feature(cfeature.BORDERS, linewidth=0.5, zorder=1001)
    ax.add_feature(cfeature.LAND, facecolor='#2e2e2e', edgecolor='white', zorder=1000)

    gl = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gl.top_labels = False   # suppress top labels
    gl.right_labels = False  # suppress right labels
    ax.set_extent([lon.min(), lon.max(), lat.min(), lat.max()], crs=ccrs.PlateCarree(central_longitude = 180))

    # Normalization: center at 0
    norm = mcolors.TwoSlopeNorm(
        vmin=uwind_anomaly_2d.min(),
        vcenter=0,
        vmax=uwind_anomaly_2d.max()
    )

    mesh = ax.pcolormesh(
        lon, lat, uwind_anomaly_2d,
        cmap='coolwarm',
        norm = norm,
        transform=ccrs.PlateCarree(),
        shading='auto'
    )

    # Shift longitude coords
    uwind_anomaly_shifted = uwind_anomaly_2d.assign_coords(
        lon=(((uwind_anomaly_2d.lon + 180) % 360) - 180)
    ).sortby("lon")

    # Highlight thresholds
    for val, color in zip([-20, -15, -10, -5, 0, 5, 10, 15, 20], ["magenta", "#0717f7", "blue", "#7982f7", "grey", "#f77979", "red", "#b81414", "crimson"]):
        cs = ax.contour(uwind_anomaly_shifted.lon, uwind_anomaly_shifted.lat, uwind_anomaly_shifted, levels=[val], colors=[color], linewidths=2, transform=ccrs.PlateCarree())
        ax.clabel(cs, fmt={val: f"{val}"}, inline=True, fontsize=10)
        
    plt.colorbar(mesh, ax=ax, orientation='horizontal', pad=0.03, shrink=0.6, label='U-wind anomaly (m/s)')

    plt.title(f'NCEP NCAR 2.5deg {pressure_level} hPa U-wind anomaly over 20N-20S', fontsize=16, loc='left')
    plt.title(f'{year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}00 UTC', fontsize=16, loc='right')
    plt.tight_layout()
    image_path = f'uwind_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)
    
@bot.command(name='gfs_streamlines')
async def gfs_streamlines(ctx, btkID:str, mb:int=200):
    import urllib3
    from bs4 import BeautifulSoup
    from datetime import datetime

    btkID = btkID.lower()
    def _00x_to_xx00(des):
        convert_map = {"l": "al", "e": "ep", "c": "cp", "w":"wp", "a":"io", "b":"io", "s":"sh", "p":"sh"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[a-z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    #http = urllib3.PoolManager(cert_reqs='CERT_NONE')

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    basinDate = datetime.now()
    basinmonth = basinDate.month
    basinYear = basinDate.year
    if btkID[:2] in ['sh', 'wp', 'io']:
        if btkID[:2] == 'sh':
            if basinmonth >= 7:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear+1}.dat'
            else:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
        else:
            btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
    else:
        btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'

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

    await ctx.send("Storm located, generating grib data from NCEP NOMAD...")
    centerX, centerY = cdx[-1], cdy[-1]
    copyX = centerX + 360 if centerX < 0 else centerX
    DateTime = list(dict.fromkeys(DateTime))
    year, month, day, hour, minutes, seconds = map(int, DateTime[-2].replace('-', ' ').replace(':', ' ').split()) #Get the previous 6 hour slot to allow access to GFS model...
    print(DateTime[-2])
    url = f'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?dir=%2Fgfs.{year}{month:02d}{day:02d}%2F{hour:02d}%2Fatmos&file=gfs.t{hour:02d}z.pgrb2.0p25.f006&var_UGRD=on&var_VGRD=on&lev_{mb}_mb=on&lev_10_mb=on&subregion=&toplat={centerY+10}&leftlon={copyX-10}&rightlon={copyX+10}&bottomlat={centerY-10}'
    
    import requests
    filename = 'gfs_data'
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Data successfully downloaded to {filename}")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"An error occurred while downloading the data: {e}")
        return

    # This code downloads GFS data for a specific latitude and longitude.
    # It constructs the URL for the GFS data, ensuring the longitude is in the correct range.
    # It then uses the requests library to fetch the data and save it to a file.

    import xarray as xr
    try:
        ds = xr.open_dataset(filename, engine='cfgrib')
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"An error occurred while loading the dataset: {e}")

    ds.to_netcdf('gfs_data.nc')
    print("Data saved to gfs_data.nc")

    u_wind, v_wind = ds['u'], ds['v']
    longitude, latitude = ds['longitude'], ds['latitude']

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import matplotlib.style as mplstyle
    mplstyle.use("dark_background") 

    # Select data for input mb pressure level
    u_200mb, v_200mb = u_wind.sel(isobaricInhPa=mb), v_wind.sel(isobaricInhPa=mb)
    longitude = xr.where(longitude < 0, longitude + 180, longitude - 180)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree(central_longitude=180))
    ax.set_extent([longitude.min(), longitude.max(), latitude.min(), latitude.max()], crs=ccrs.PlateCarree(central_longitude=180))
    from matplotlib import colors      
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))

    # Plot streamlines
    ax.streamplot(longitude, latitude, u_200mb.values, v_200mb.values, color='w',transform=ccrs.PlateCarree(central_longitude=180))
    ax.scatter(copyX, centerY, color='r', marker='x', s=100, zorder=7860, transform=ccrs.PlateCarree())

    # Add coastlines and gridlines
    ax.coastlines()
    import matplotlib.ticker as mticker
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    ax.set_xlabel('Longitude (degrees)')
    ax.set_ylabel('Latitude (degrees)')
    gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gls.top_labels = False
    gls.right_labels = False
    gls.xlocator = mticker.FixedLocator(range(-180, 181, 2))  # Control gridline spacing
    gls.ylocator = mticker.FixedLocator(range(-90, 91, 2))
    #gl.xformatter = LONGITUDE_FORMATTER
    gls.yformatter = LATITUDE_FORMATTER
    gls.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
    gls.ylabel_style = {'size': 8, 'color': 'w'}

    import os
    ax.set_title(f"GFS Streamlines at {mb} mb for {btkID.upper()} {stormName}\nATCF Time: {DateTime[-1]} | GFS Run Time: {DateTime[-2]}, Forecast Tau +6", fontsize=12, color='w')
    plt.tight_layout()
    image_path = f'{btkID}_SST_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)
    
    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)
    import glob
    os.remove(filename)  # Clean up the downloaded file
    paths_to_remove = sorted(glob.glob('gfs_data.*'))
    for path in paths_to_remove:
        os.remove(path)  # Clean up any additional files created by cfgrib

@bot.command(name='tchp')
async def tchp(ctx, btkID:str):
    import urllib3
    from bs4 import BeautifulSoup
    from datetime import datetime

    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
    btkID = btkID.lower()
    def _00x_to_xx00(des):
        convert_map = {"l": "al", "e": "ep", "c": "cp", "w":"wp", "a":"io", "b":"io", "s":"sh", "p":"sh"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[a-z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    #http = urllib3.PoolManager(cert_reqs='CERT_NONE')

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    basinDate = datetime.now()
    basinmonth = basinDate.month
    basinYear = basinDate.year
    if btkID[:2] in ['sh', 'wp', 'io']:
        if btkID[:2] == 'sh':
            if basinmonth >= 7:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear+1}.dat'
            else:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
        else:
            btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
    else:
        btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'

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
    await ctx.send("Storm located, generating tchp data from OpenDAP...")
    centerX, centerY = cdx[-1], cdy[-1]

    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import os
  
    # Load dataset
    url = f"https://cwcgom.aoml.noaa.gov/thredds/dodsC/TCHP/TCHP.nc"
    ds = xr.open_dataset(url)
    await ctx.send("Data loaded, plotting values...")
    tchp = ds["Tropical_Cyclone_Heat_Potential"].isel(time=-1)
    time_str = str(tchp.time.values).split("T")[0]
    time_of_day_str = str(tchp.time.values).split("T")[1]

    # Subset region with valid data
    ohc_subset = tchp.sel(lat=slice(centerY-10, centerY+10), lon=slice(centerX-10, centerX+10))
    # Create figure and map axis
    fig = plt.figure(figsize=(13, 7))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([centerX-10, centerX+10, centerY-10, centerY+10], crs=ccrs.PlateCarree())

    # Plot filled contours
    levels = np.arange(0, 193, 1)
    cf = ax.contourf(
        ohc_subset.lon,
        ohc_subset.lat,
        ohc_subset,
        levels=levels,
        cmap="turbo",
        vmin=0,
        vmax=193,
        extend="both"
    )

    # Dynamically align colorbar to map height
    pos = ax.get_position()
    cbar_ax = fig.add_axes([pos.x1 + 0.02, pos.y0, 0.02, pos.height])
    cbar = plt.colorbar(cf, cax=cbar_ax, orientation="vertical", label="TCHP (kJ/cm²)")
    cbar.set_ticks(np.arange(0, 193, 25))

    # Highlight thresholds
    for val, color in zip([16, 60, 100, 125, 160], ["cyan", "green", "brown", "red", "black"]):
        cs = ax.contour(ohc_subset.lon, ohc_subset.lat, ohc_subset, levels=[val], colors=[color], linewidths=2)
        ax.clabel(cs, fmt={val: f"{val}"}, inline=True, fontsize=10)

    # Add land and gridlines
    from matplotlib import colors      
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gl.top_labels = False   # suppress top labels
    gl.right_labels = False  # suppress right labels
    
    relevant_val = ohc_subset.sel(lat=centerY, lon=centerX, method="nearest").values.item()

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='x', color='r', label=f'TCHP Value over storm: {relevant_val:.2f} kJ/cm²', markerfacecolor='#444764', markersize=10),
        
    ]
    if relevant_val < 125:
        ax.scatter(centerX, centerY, color='r', marker='x', s=100, zorder=10, transform=ccrs.PlateCarree())
    else:
        ax.scatter(centerX, centerY, color='k', marker='x', s=100, zorder=10, transform=ccrs.PlateCarree())
    # Title
    ax.set_title(f"Tropical Cyclone Heat Potential (TCHP) for {btkID.upper()} {stormName} | ATCF Time: {DateTime[-1]}\nTime of latest reading: {time_str} {time_of_day_str[:8]} UTC", fontsize=12)
    ax.legend(handles=legend_elements, loc='upper right')
    plt.tight_layout()
    image_path = f'{btkID}_SST_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)

@bot.command(name='tchp_custom')
async def tchp_custom(ctx, centerY:float, centerX:float):
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import os

    await ctx.send("Data received...")
    # Load dataset
    url = f"https://cwcgom.aoml.noaa.gov/thredds/dodsC/TCHP/TCHP.nc"
    ds = xr.open_dataset(url)
    await ctx.send("Data loaded, plotting values...")
    tchp = ds["Tropical_Cyclone_Heat_Potential"].isel(time=-1)
    time_str = str(tchp.time.values).split("T")[0]
    time_of_day_str = str(tchp.time.values).split("T")[1]

    # Subset region with valid data
    ohc_subset = tchp.sel(lat=slice(centerY-10, centerY+10), lon=slice(centerX-10, centerX+10))
    # Create figure and map axis
    fig = plt.figure(figsize=(13, 7))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([centerX-10, centerX+10, centerY-10, centerY+10], crs=ccrs.PlateCarree())

    # Plot filled contours
    levels = np.arange(0, 193, 1)
    cf = ax.contourf(
        ohc_subset.lon,
        ohc_subset.lat,
        ohc_subset,
        levels=levels,
        cmap="turbo",
        vmin=0,
        vmax=193,
        extend="both"
    )

    # Dynamically align colorbar to map height
    pos = ax.get_position()
    cbar_ax = fig.add_axes([pos.x1 + 0.02, pos.y0, 0.02, pos.height])
    cbar = plt.colorbar(cf, cax=cbar_ax, orientation="vertical", label="TCHP (kJ/cm²)")
    cbar.set_ticks(np.arange(0, 193, 25))

    # Highlight thresholds
    for val, color in zip([16, 60, 100, 125, 160], ["cyan", "green", "brown", "red", "black"]):
        cs = ax.contour(ohc_subset.lon, ohc_subset.lat, ohc_subset, levels=[val], colors=[color], linewidths=2)
        ax.clabel(cs, fmt={val: f"{val}"}, inline=True, fontsize=10)

    # Add land and gridlines
    from matplotlib import colors      
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gl.top_labels = False   # suppress top labels
    gl.right_labels = False  # suppress right labels
    
    relevant_val = ohc_subset.sel(lat=centerY, lon=centerX, method="nearest").values.item()

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='x', color='r', label=f'TCHP Value over storm: {relevant_val:.2f} kJ/cm²', markerfacecolor='#444764', markersize=10),    
    ]

    if relevant_val < 125:
        ax.scatter(centerX, centerY, color='r', marker='x', s=100, zorder=10, transform=ccrs.PlateCarree())
    else:
        ax.scatter(centerX, centerY, color='k', marker='x', s=100, zorder=10, transform=ccrs.PlateCarree())
    
    # Title
    ax.set_title(f"Tropical Cyclone Heat Potential (TCHP) for ({centerY}, {centerX})\nTime of latest reading: {time_str} {time_of_day_str[:8]} UTC", fontsize=12)
    ax.legend(handles=legend_elements, loc='upper right')
    plt.tight_layout()
    image_path = f'_SST_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)

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
    from matplotlib import cm
    from matplotlib.colors import ListedColormap, LinearSegmentedColormap
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
    btkID = btkID.lower()
    def _00x_to_xx00(des):
        convert_map = {"l": "al", "e": "ep", "c": "cp", "w":"wp", "a":"io", "b":"io", "s":"sh", "p":"sh"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[a-z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    #http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    def crw():
        newcmp = LinearSegmentedColormap.from_list("", [
        (0/40, '#48003f'),
        (5/40, "#910087"),
        (5/40, "#280096"),
        (10/40, "#6a5bbf"),
        (10/40, "#000082"),
        (15/40, "#005aff"),
        (15/40, "#0075ff"),
        (20/40, "#00edff"),
        (20/40, "#00ff00"),
        (27/40, "#00a100"),
        (27/40, "#dff200"),
        (30/40, "#d56900"),
        (30/40, "#dc5a00"),
        (35/40, "#730000"),
        (35/40, "#c86432"),
        (40/40, "#542e15")])
        vmax = 40
        vmin = 0

        return newcmp, vmax, vmin


    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    async def generate_and_send_image(btkID, DateTime, centerX, centerY, stormName):
        # Generate the SST map image
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        import cartopy.feature as cfeature
        from matplotlib import colors
        
        ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
        ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
        ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels = False   # suppress top labels
        gls.right_labels = False  # suppress right labels

        # Plot SST data from 10 degC to 35 degC
        col, vm, vn = crw()
        c = ax.contourf(lon, lat, sst, levels=np.arange(vn, vm, 1), transform=ccrs.PlateCarree(), cmap=col, extend='both')
        # Add small contour lines for all SSTs
        contour = ax.contour(lon, lat, sst, levels=np.arange(vn, vm, 1), colors='black', linewidths=0.5, transform=ccrs.PlateCarree())
        # Add a contour line for 26 degrees Celsius

        contour_level = 26
        contour = ax.contour(lon, lat, sst, levels=[contour_level], colors='black', linewidths=2, transform=ccrs.PlateCarree())

        plt.colorbar(c, label='Sea Surface Temperature (°C)')

        # Extract closest center value 
        lat_idx = (np.abs(lat - centerY)).argmin()
        lon_idx = (np.abs(lon - centerX)).argmin()

        # Extract the SST value at that grid point
        sst_value = sst[lat_idx, lon_idx]


        legend_elements = [
            Line2D([0], [0], marker='x', color='k', label=f'SSTs over storm: {sst_value:.2f}°C', markerfacecolor='#444764', markersize=10),
            Line2D([0], [0], marker='_', color='k', label='26 degC SST Isotherm', markerfacecolor='#444764', markersize=10),
        ]

        plt.scatter(centerX, centerY, color='k', marker='x', zorder=10000000)
        ax.set_extent([centerX - 10, centerX + 10, centerY - 10, centerY + 10], crs=ccrs.PlateCarree())
        plt.title(f'SST Map over {btkID.upper()} {stormName} | ATCF Time: {DateTime[-1]}')
        ax.legend(handles=legend_elements, loc='upper center')
        plt.tight_layout()
        image_path = f'{btkID}_SST_Map.png'
        plt.savefig(image_path, format='png')
        plt.close()

        # Send the generated image
        await send_image(image_path)

        # Remove the temporary image file
        os.remove(image_path)

    from datetime import datetime
    basinDate = datetime.now()
    basinmonth = basinDate.month
    basinYear = basinDate.year
    if btkID[:2] in ['sh', 'wp', 'io']:
        if btkID[:2] == 'sh':
            if basinmonth >= 7:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear+1}.dat'
            else:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
        else:
            btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
    else:
        btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'

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
    two_days_ago = current_date - timedelta(days=3)

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
    from matplotlib import cm
    from matplotlib.colors import ListedColormap, LinearSegmentedColormap

    if centerY < -90 or centerY > 90 or centerX > 179.99 or centerX < -179.99:
        await ctx.send("Out of bounds!")
        return

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def crw():
        newcmp = LinearSegmentedColormap.from_list("", [
        (0/40, '#48003f'),
        (5/40, "#910087"),
        (5/40, "#280096"),
        (10/40, "#6a5bbf"),
        (10/40, "#000082"),
        (15/40, "#005aff"),
        (15/40, "#0075ff"),
        (20/40, "#00edff"),
        (20/40, "#00ff00"),
        (27/40, "#00a100"),
        (27/40, "#dff200"),
        (30/40, "#d56900"),
        (30/40, "#dc5a00"),
        (35/40, "#730000"),
        (35/40, "#c86432"),
        (40/40, "#542e15")])
        vmax = 40
        vmin = 0

        return newcmp, vmax, vmin

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    async def generate_and_send_image(centerX, centerY):
        # Generate the SST map image
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        ax.coastlines()
        import cartopy.feature as cfeature
        from matplotlib import colors
        
        ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
        ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
        ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels = False   # suppress top labels
        gls.right_labels = False  # suppress right labels

        # Plot SST data from 10 degC to 35 degC
        col, vm, vn = crw()
        c = ax.contourf(lon, lat, sst, levels=np.arange(vn, vm, 1), transform=ccrs.PlateCarree(), cmap=col, extend='both')
        # Add small contour lines for all SSTs
        contour = ax.contour(lon, lat, sst, levels=np.arange(vn, vm, 1), colors='black', linewidths=0.5, transform=ccrs.PlateCarree())

        # Add a contour line for 26 degrees Celsius
        contour_level = 26
        contour = ax.contour(lon, lat, sst, levels=[contour_level], colors='black', linewidths=2, transform=ccrs.PlateCarree())

        plt.colorbar(c, label='Sea Surface Temperature (°C)')

        # Extract closest center value 
        lat_idx = (np.abs(lat - centerY)).argmin()
        lon_idx = (np.abs(lon - centerX)).argmin()

        # Extract the SST value at that grid point
        sst_value = sst[lat_idx, lon_idx]

        legend_elements = [
            Line2D([0], [0], marker='x', color='k', label=f'SSTs over Storm location: {sst_value:.2f}°C', markerfacecolor='#444764', markersize=10),
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
    two_days_ago = current_date - timedelta(days=3)

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

@bot.command(name='tcsst_historical')
async def tcsst_historical(ctx, centerY: float, centerX: float, date, offset=0):
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
    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
    if centerY < -90 or centerY > 90 or centerX > 179.99 or centerX < -179.99:
        await ctx.send("Out of bounds!")
        return

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def crw():
        return LinearSegmentedColormap.from_list("", [
            (0/40, '#48003f'),
            (5/40, "#910087"),
            (5/40, "#280096"),
            (10/40, "#6a5bbf"),
            (10/40, "#000082"),
            (15/40, "#005aff"),
            (15/40, "#0075ff"),
            (20/40, "#00edff"),
            (20/40, "#00ff00"),
            (27/40, "#00a100"),
            (27/40, "#dff200"),
            (30/40, "#d56900"),
            (30/40, "#dc5a00"),
            (35/40, "#730000"),
            (35/40, "#c86432"),
            (40/40, "#542e15")]), 40, 0

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            await ctx.send(file=discord.File(image_file))

    async def generate_and_send_image(centerX, centerY, lon, lat, sst):
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        ax.coastlines()
        import cartopy.feature as cfeature
        from matplotlib import colors
        
        ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
        ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
        ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels = gls.right_labels = False

        col, vm, vn = crw()
        c = ax.contourf(lon, lat, sst, levels=np.arange(vn, vm, 1), transform=ccrs.PlateCarree(), cmap=col, extend='both')
        ax.contour(lon, lat, sst, levels=np.arange(vn, vm, 1), colors='black', linewidths=0.5, transform=ccrs.PlateCarree())
        ax.contour(lon, lat, sst, levels=[26], colors='black', linewidths=2, transform=ccrs.PlateCarree())

        plt.colorbar(c, label='Sea Surface Temperature (°C)')
        # Extract closest center value 
        lat_idx = (np.abs(lat - centerY)).argmin()
        lon_idx = (np.abs(lon - centerX)).argmin()

        # Extract the SST value at that grid point
        sst_value = sst[lat_idx, lon_idx]

        legend_elements = [
            Line2D([0], [0], marker='x', color='k', label=f'SSTs over Center location: {sst_value:.2f}°C', markerfacecolor='#444764', markersize=10),
            Line2D([0], [0], marker='_', color='k', label='26 degC SST Isotherm', markersize=10),
        ]
        plt.scatter(centerX, centerY, color='k', marker='x', zorder=10000000)

        ax.set_extent([centerX - offset if offset else centerX - 10,
                       centerX + offset if offset else centerX + 10,
                       centerY - offset if offset else centerY - 10,
                       centerY + offset if offset else centerY + 10], crs=ccrs.PlateCarree())

        plt.title(f'SST Map over ({centerY}, {centerX}) on {date}:')
        ax.legend(handles=legend_elements, loc='upper center')
        plt.tight_layout()
        image_path = 'SST_Map.png'
        plt.savefig(image_path, format='png')
        plt.close()

        await send_image(image_path)
        os.remove(image_path)

    try:
        day, month, year = date.split('/')
        int_day, int_month, int_year = int(day), int(month), int(year)
        given_date = datetime(int_year, int_month, int_day)
    except ValueError:
        await ctx.send("Invalid date format. Use DD/MM/YYYY.")
        return

    today = datetime.utcnow()
    if given_date.date() > (today.date() - timedelta(days=15)):
        file_suffix = "_preliminary.nc"
    else:
        file_suffix = ".nc"

    url = f"https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{year}{month.zfill(2)}/oisst-avhrr-v02r01.{year}{month.zfill(2)}{day.zfill(2)}{file_suffix}"

    # Download NetCDF file
    response = http.request('GET', url)
    if response.status != 200 or b'<!DOCTYPE html>' in response.data[:200]:
        await ctx.send("Failed to retrieve valid NetCDF file. The file may not exist for the given date.")
        return

    with open('sst_data.nc', 'wb') as file:
        file.write(response.data)

    try:
        dataset = netCDF4.Dataset('sst_data.nc')
        lat = dataset.variables['lat'][:]
        lon = dataset.variables['lon'][:]
        sst = dataset.variables['sst'][0, 0, :, :]  # Convert from Kelvin if needed
        await generate_and_send_image(centerX, centerY, lon, lat, sst)
        dataset.close()
    except Exception as e:
        await ctx.send(f"Failed to process NetCDF data: {e}")
    finally:
        if os.path.exists('sst_data.nc'):
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
    import sys
    from urllib.request import build_opener

    await ctx.send("Please wait as the data loads.")
    if year < 1854 or year > 2024:
        await ctx.send("The data for this year does not exist.")
        return
    
    month_f = str(month).zfill(2)
    '''
    opener = build_opener()
    filelist = [
        f'https://data.rda.ucar.edu/ds277.9/ersst.v5.nc/ersst.v5.{year}{month_f}.nc'
    ]

    for file in filelist:
        ofile = os.path.basename(file)
        sys.stdout.write("downloading " + ofile + " ... ")
        sys.stdout.flush()
        infile = opener.open(file)
        outfile = open(ofile, "wb")
        outfile.write(infile.read())
        outfile.close()
        sys.stdout.write("done\n")
    '''
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
    
    def _00x_to_xx00(des):
        convert_map = {"L": "AL", "E": "EP", "C": "CP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[A-Z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    IBTRACS_ID = f"{btkID}{yr}"
    basin = ""
    atcf_id = ""
    year = ""
    name = ""
    flag = False
    atcfID = []
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
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
    header_20XX = {"AL":"L", "EP":"E", "CP":"C", "WP":"W", "AS":"A", "BB":"B", "SH":"S", "SI":"S", "SP":"P", "IO":"B"}
    
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
    
    def _00x_to_xx00(des):
        convert_map = {"L": "AL", "E": "EP", "C": "CP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[A-Z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    IBTRACS_ID = f"{btkID}{yr}"
    basin = ""
    atcf_id = ""
    year = ""
    name = ""
    flag = False
    atcfID = []
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
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
    
@bot.command(name='digty_image')
async def digty_image(ctx, name:str, yr:str, hour:str, day:str,  month:str, imageYear:str, enhancement:str, satellite:str):
    name = name.upper()
    month = month.zfill(2)
    day = day.zfill(2)
    hour = hour.zfill(2)
    if enhancement == 'BD' or enhancement == 'NHC':
        enhancement = enhancement.lower()
    elif enhancement == 'ir1-ir2' or enhancement == 'ir4-ir1':
        enhancement = enhancement.upper()
    else:
        enhancement = enhancement.upper()
    satellite = satellite.upper()

    satelliteMap = {'GMS1':'GMS1', 'GMS2':'GMS2', 'GMS3':'GMS3', 'GMS4':'GMS4', 'GMS5':'GMS5', 'GOE9':'GOE9', 'MTS1':'MTS1', 'MTS2':'MTS2', 'HMW8':'HMW8', 'HMW9':'HMW9'}
    enhancementMap = {'VIS':'0', 'IR1':'1', 'IR2':'2', 'IR3': '3', 'IR4': '4', 'BD': 'bd', 'bd': 'bd', 'nhc': 'nhc', 'NHC':'nhc', 'IR1-IR2': 'IR1-IR2', 'IR4-IR1': 'IR4-IR1'}

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

    url = f"http://agora.ex.nii.ac.jp/digital-typhoon/wnp/by-name/{jma}/{enhancementMap[enhancement]}/512x512/{satelliteMap[satellite]}{imageYear[2:]}{month}{day}{hour}.{jma}.jpg"
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
    import matplotlib.colors as mcolors
    import matplotlib.ticker as mticker
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
    print(f"Command received from server: {ctx.guild.name}")
    btkID = btkID.upper()
    if btkID == 'BENTO':
        btkID = 'BENTOJANA'
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'VICKY 2020', 'JOYCE 2018', 'GORDON 1979', 'BENI 2003', 'MARK 1992', 'NADINE 1978',
                  'WINNIE 1978', 'HARVEY 2005', 'FREDA 1981', 'POLLY 1971', 'LOUISE 1970', 'LUCY 1962', 'CARMEN 1974']
    check = f"{btkID} {yr}"
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    if(btkID == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    if(btkID == 'UNNAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    
    def _00x_to_xx00(des):
        convert_map = {"L": "AL", "E": "EP", "C": "CP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[A-Z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    #Load in the loops for finding the latitude and longitude...
    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, winds, status, timeCheck, DateTime = [], [], [], [], [], []
    storm_name = ""
    s_ID = ""
    idl = False

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4] and len(lines[20])>1):
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

    if len(winds) == 0:
        await ctx.send("Error 404: Storm not found. Please check if your entry is correct.")
        return

    await ctx.send("System located in database, generating track...")
    print("System located in database, generating track...")
    
    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

    from matplotlib import colors
    
    ax.add_feature(cfeature.COASTLINE, linewidth=1, color="c")
    ax.add_feature(cfeature.BORDERS, color="w", linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    if idl == False:
        ax.add_feature(cfeature.OCEAN, facecolor='#191919')

    if idl != True:
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
    '''
        if ratio < 0.3: 
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
        elif ratio > 0.7:
            ax.set_xlim(center_x-(center_height), center_x+(center_height))
            ax.set_ylim(center_y-center_height, center_y+center_height)
        else:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-center_height, center_y+center_height)
        '''
    #----NEW-----
    ax.set_xlim(minLong-8, maxLong+8)
    ax.set_ylim(minLat-2, maxLat+2)
    if idl == True:
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.xlocator = mticker.FixedLocator(range(-180, 181, 10))  # Control gridline spacing
        gl.ylocator = mticker.FixedLocator(range(-90, 91, 10))
        #gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
        gl.ylabel_style = {'size': 8, 'color': 'w'}
    
    #------------
    #---MODDED---
    #Defining the legend box for the plot...
    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='Non-Tropical',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='Sub-Tropical',markerfacecolor='#444764', markersize=10),
    ]

    # Define the color mapping for wind speeds
    colors = ['b', 'g', '#ffff00', '#ffa001', '#ff5908', 'r', 'm']
    bounds = [0, 34, 64, 81, 96, 112, 137, 200]
    norm = mcolors.BoundaryNorm(bounds, len(colors))
    labels = ['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5']
    #------------
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

    plt.plot(LineX, LineY, color="w", linestyle="-")
    plt.text(LineX[0], LineY[0], f'{DateTime[0]}')
    plt.text(LineX[len(LineX)-1], LineY[len(LineX)-1], f'{DateTime[len(LineX)-1]}')

    #Applying final touches...
    print("Printing image...")
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    if s_ID == ' ':
        plt.title(f'{storm_name} {yr}')
    else:
        plt.title(f'{s_ID} {storm_name}')
    plt.title(f'VMAX: {vmax} Kts', loc='left', fontsize=9)
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right', fontsize=9)
    ax.legend(handles=legend_elements, loc="upper left")
    if idl == True:
        plt.grid(True)

    #-----NEW-----------
    # Create the colorbar
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Add colorbar to the plot
    cbar = plt.colorbar(sm, ticks=bounds, orientation='horizontal', pad=0.05, aspect=50, ax=ax, shrink=0.5)
    cbar.set_label('SSHWS Windspeeds (Kts)')
    cbar.ax.set_xticklabels(['0', '34', '64', '81', '96', '112', '137', '200'])
    #---------------------
    plt.tight_layout()
    
    r = np.random.randint(1, 10)
    image_path = f'Track_Map{r}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)  

@bot.command(name='mjoplot')
async def mjoplot(ctx, day:int, month:int, year:int):
    import urllib3
    import matplotlib.pyplot as plt
    from bs4 import BeautifulSoup
    import numpy as np
    import math
    import os
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
    if (day <2 and month < 1 and year <= 1940) or (month > 8 and year >= 2023):
        await ctx.send("Data is not available for this timeframe yet on ECMWF ERAv5.")
        return

    await ctx.send("Please be patient as the data is retrieved.")

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    url = 'https://www.psl.noaa.gov/mjo/mjoindex/omi.era5.1x.webpage.4023.txt'
    

    def fetch_data(url):
        response = http.request('GET', url)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    mjo_data = fetch_data(url)
    parsed_data = parse_data(mjo_data)

    mjo_data = []
    parsed_lines = parsed_data.split('\n')
    i, limit = 0, 10
    for line in parsed_lines:
        if line:
            mjo_data = line.split()
            if mjo_data[0] == str(year) and mjo_data[1] == str(month) and mjo_data[2] == str(day):
                break
            else:
                mjo_data = []

    await ctx.send("Data successfully retrieved, plotting phase diagram...")

    #Plot inner circle of suppresed MJO
    circle = plt.Circle((0, 0), 1, fill=False)
    fig, ax = plt.subplots()
    ax.add_patch(circle)
    plt.grid(color='gray', linestyle=':')
    plt.axis('scaled')

    #Plot MJO value
    plt.scatter(float(mjo_data[4]), -1*float(mjo_data[3]), marker='o', color='r', s=45, zorder=99)
    #          x (RMM PC1) = OMI PC2   y (RMM PC2) = - OMI PC1

    #Plot the y = x line split
    x1 = np.arange(-5, 1*math.cos(5*math.pi/4)+0.1, 0.1)
    x2 = np.arange(1*math.cos(math.pi/4), 5, 0.1)
    y1 = x1 # y = x
    y2 = x2 # y = x
    plt.plot(x1, y1, color='w') 
    plt.plot(x2, y2, color='w') 

    #Plot the y = -x line split
    x3 = np.arange(-5, 1*math.cos(3*math.pi/4)+0.1, 0.1)
    x4 = np.arange(1*math.cos(7*math.pi/4), 5, 0.1)
    y3 = -x3
    y4 = -x4
    plt.plot(x3, y3, color='w') 
    plt.plot(x4, y4, color='w') 

    #Plot x-axis
    x5 = np.arange(-5, -0.9, 0.1)
    x6 = np.arange(1, 5, 0.1)
    y5 = np.zeros_like(x5)
    y6 = np.zeros_like(x6)
    plt.plot(x5, y5, color='w') 
    plt.plot(x6, y6, color='w') 

    #Plot y-axis
    x7 = np.arange(-5, -0.9, 0.1)
    x8 = np.arange(1, 5, 0.1)
    plt.plot(np.zeros_like(x7), x7, color='w')
    plt.plot(np.zeros_like(x8), x8, color='w')

    #Plot the phase numbers:
    plt.text(-3.5, -1.33, '1')
    plt.text(-1.5, -3.5, '2')
    plt.text(1.5, -3.5, '3')
    plt.text(3.5, -1.33, '4')
    plt.text(3.5, 1.33, '5')
    plt.text(1.5, 3.5, '6')
    plt.text(-1.5, 3.5, '7')
    plt.text(-3.5, 1.67, '8')

    #Plot the region text:
    plt.text(-0.7, -3.9, 'Indian\nOcean', color='green', size=12, fontweight='bold')
    plt.text(-0.7, 3.2, 'Western\nPacific', color='magenta', size=12, fontweight='bold')
    plt.text(-3.9, -1, 'Western Hem.\n& Africa', color='blue', size=12, rotation=90, fontweight='bold')
    plt.text(3.1, -1, 'Maritime\nContinent', color='brown', size=12, rotation=270, fontweight='bold')

    monthMap = {1:"January", 2: "February", 3:"March", 4:"April",
                5:"May", 6:"June", 7:"July", 8:"August",
                9: "September", 10:"October", 11:"November", 12:"December"}

    plt.xlim(-4, 4)
    plt.ylim(-4, 4)
    plt.title(f'MJO Phase Diagram for {day} {monthMap[month]} {year}')
    plt.xlabel("RMM PC1 component")
    plt.ylabel("RMM PC2 component")
    r = np.random.randint(1, 10)
    image_path = f'MJO{r}.png'
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
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
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

@bot.command(name='findobs')
async def findobs(ctx, lat: float, long: float):
    import pandas as pd
    import os
    from datetime import datetime, timedelta
    await ctx.send("Due to the large database being accessed, this command will take a little while (ETA: 30 seconds) to load.")
    
    # Define the URL to load the CSV data
    url = f"https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_rt_60.csv?platform_code,platform_type,latitude,longitude,time&latitude>={lat-1}&latitude<={lat+1}&longitude>={long-1}&longitude<={long+1}"

    # Read the CSV content from the URL
    data = pd.read_csv(url)

    # Drop the first row (index 0) which contains header information
    data = data.drop(index=0)

    # Reset the index after dropping the row
    data.reset_index(drop=True, inplace=True)

    # Convert 'time' column to datetime, ensuring proper parsing
    data['time'] = pd.to_datetime(data['time'], utc=True, errors='coerce')

    # Get the current date and the previous day as pandas datetime64 objects
    now = pd.Timestamp.utcnow()
    yesterday = now - timedelta(days=1)

    # Filter observations to keep only those from the previous and current day
    filtered_data = data[(data['time'] >= yesterday) & (data['time'] <= now)]

    # Drop duplicates based on 'platform_code' to keep only unique station IDs
    distinct_stations = filtered_data[['platform_code', 'platform_type', 'latitude', 'longitude']].drop_duplicates(subset='platform_code')
    await ctx.send("Data request successful.")

    # Save the filtered data to a CSV file
    output_file = "platform_data_find.csv"
    distinct_stations.to_csv(output_file, index=False)

    # Send the CSV file as an attachment in Discord
    with open(output_file, "rb") as output_file:
        await ctx.send(file=discord.File(output_file))

    # Delete the temporary CSV file
    os.remove("platform_data_find.csv")

@bot.command(name='obsplot')
async def obsplot(ctx, stationID:str):
    import pandas as pd
    import matplotlib.pyplot as plt
    import os 

    await ctx.send("Due to the large database this is looking at, it may take time to search for the obs. Please be patient.")

    # Define the URL from which to load the CSV data
    url = f"https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_rt_60.csv?platform_code,platform_type,latitude,longitude,time,slp&orderBy(%22time%22)&platform_code=%22{str(stationID)}%22"

    
    # Read the CSV content from the URL, keeping all rows
    data = pd.read_csv(url)

    # Drop the first row (index 0)
    data = data.drop(index=0)

    # Reset the index after dropping the row
    data.reset_index(drop=True, inplace=True)

    # Display the first few rows and the columns of the DataFrame
    print(data.head())
    print("Columns after reading CSV:", data.columns.tolist())

    # Convert 'time' to datetime, handling UTC
    data['time'] = pd.to_datetime(data['time'], utc=True)

    # Convert 'slp' to numeric, forcing errors to NaN
    data['slp'] = pd.to_numeric(data['slp'], errors='coerce')

    # Drop rows where 'slp' is NaN
    data_clean = data.dropna(subset=['slp'])

    # Find the minimum recorded pressure and its corresponding time
    min_pressure = data_clean['slp'].min()
    min_pressure_time = data_clean[data_clean['slp'] == min_pressure]['time'].iloc[0]

    await ctx.send("Data request successful, plotting data...")
    # Plotting the SLP vs Time
    plt.figure(figsize=(12, 6))
    plt.plot(data_clean['time'], data_clean['slp'], marker='o', linestyle='-', color='b')
    plt.title(f'Time vs Sea Level Pressure (SLP) series of Station {stationID}\nMinimum Pressure: {min_pressure:.2f} hPa at {min_pressure_time.strftime("%Y-%m-%d %H:%M")}')
    plt.xlabel('Time (Date)')
    plt.ylabel('Sea Level Pressure (hPa)')
    plt.xticks(rotation=45)
    plt.grid()
    image_path = f'obsplot_{stationID}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)

@bot.command(name='storm_name')
async def storm_name(ctx, name:str):
    import csv
    import os
    name = name.upper()
    ID = ""

    resultYr = []
    await ctx.send("Hold as the database is accessed.")
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
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
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
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
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
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
    #print(cdx, "\n", cdy, "\n", winds, "\n", status, "\n", timeCheck, "\n", storm_name, "\n", id)
    #-----------------------------------------------------------------------------------
    await ctx.send("Season located in database, generating track...")
    print("Season located in database, generating track...")
    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

    from matplotlib import colors
    
    ax.add_feature(cfeature.COASTLINE, linewidth=1, color="c")
    ax.add_feature(cfeature.BORDERS, color="w", linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    if idl == False:
        ax.add_feature(cfeature.OCEAN, facecolor='#191919')
    if idl != True:
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
        plt.plot(LineX, LineY, color="w", linestyle="-", lw=1)
    
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
    else:  # basin == 'SP' or any specific value really 
        #Setting the coordinates for the bounding box...
        center_x = (minLong + maxLong)/2
        center_y = (minLat + maxLat)/2

        center_width = abs(maxLong - minLong)
        center_height = abs(maxLat - minLat)

        ratio = (center_height/center_width)
        print(ratio)
        ax.set_xlim(minLong-8, maxLong+8)
        ax.set_ylim(minLat-2, maxLat+2)
    
    if idl==True:
        import matplotlib.ticker as mticker
        from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.xlocator = mticker.FixedLocator(range(-180, 181, 10))  # Control gridline spacing
        gl.ylocator = mticker.FixedLocator(range(-90, 91, 10))
        #gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
        gl.ylabel_style = {'size': 8, 'color': 'w'}

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
    
    ax.legend(handles=legend_elements, loc='best')
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
    import matplotlib.colors as mcolors
    import matplotlib.ticker as mticker
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
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
        
    await ctx.send("Season located in database, generating track...")
    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))

    from matplotlib import colors
    
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    if idl == False:
        ax.add_feature(cfeature.OCEAN, facecolor='#191919')

    if idl != True:
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
        plt.plot(LineX, LineY, color="#808080", linestyle="-", lw=1)
    
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
        ax.set_xlim(minLong-8, maxLong+8)
        ax.set_ylim(minLat-2, maxLat+2)
    
    if idl==True:
        import matplotlib.ticker as mticker
        from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.xlocator = mticker.FixedLocator(range(-180, 181, 10))  # Control gridline spacing
        gl.ylocator = mticker.FixedLocator(range(-90, 91, 10))
        #gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
        gl.ylabel_style = {'size': 8, 'color': 'w'}

    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='EX/LO/DB',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='SS/SD',markerfacecolor='#444764', markersize=10),
    ]

    # Define the color mapping for wind speeds
    colors = ['b', 'g', '#ffff00', '#ffa001', '#ff5908', 'r', 'm']
    bounds = [0, 34, 64, 81, 96, 112, 137, 200]
    norm = mcolors.BoundaryNorm(bounds, len(colors))
    labels = ['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5']
    #------------


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
    #-----NEW-----------
    # Create the colorbar
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Add colorbar to the plot
    cbar = plt.colorbar(sm, ticks=bounds, orientation='horizontal', pad=0.05, aspect=50, ax=ax, shrink=0.5)
    cbar.set_label('SSHWS Windspeeds (Kts)')
    cbar.ax.set_xticklabels(['0', '34', '64', '81', '96', '112', '137', '200'])
    #---------------------
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
    import matplotlib.colors as mcolors
    import matplotlib.ticker as mticker
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
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

    #Beginning work on the actual plotting of the data:
    if idl == True:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)}, figsize=(12, 10))
    else:
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(12, 10))


    from matplotlib import colors
    
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    if idl == False:
        ax.add_feature(cfeature.OCEAN, facecolor='#191919')

    if idl != True:
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
        plt.plot(LineX, LineY, color="#808080", linestyle="-", lw=1)
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
        ax.set_xlim(minLong-8, maxLong+8)
        ax.set_ylim(minLat-2, maxLat+2)
    
    if idl==True:
        import matplotlib.ticker as mticker
        from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.xlocator = mticker.FixedLocator(range(-180, 181, 10))  # Control gridline spacing
        gl.ylocator = mticker.FixedLocator(range(-90, 91, 10))
        #gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
        gl.ylabel_style = {'size': 8, 'color': 'w'}

    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='EX/LO/DB',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='SS/SD',markerfacecolor='#444764', markersize=10),
    ]

    # Define the color mapping for wind speeds
    colors = ['b', 'g', '#ffff00', '#ffa001', '#ff5908', 'r', 'm']
    bounds = [0, 34, 64, 81, 96, 112, 137, 200]
    norm = mcolors.BoundaryNorm(bounds, len(colors))
    labels = ['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5']
    #------------

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
    #-----NEW-----------
    # Create the colorbar
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Add colorbar to the plot
    cbar = plt.colorbar(sm, ticks=bounds, orientation='horizontal', pad=0.05, aspect=50, ax=ax, shrink=0.5)
    cbar.set_label('SSHWS Windspeeds (Kts)')
    cbar.ax.set_xticklabels(['0', '34', '64', '81', '96', '112', '137', '200'])
    #---------------------

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
    from datetime import datetime, timedelta
    import requests
    from matplotlib.lines import Line2D
    import os
    import urllib3
    from bs4 import BeautifulSoup
    import numpy as np
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
    await ctx.send("Please hold as the data is generated.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    #http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()
    
    btkID = btkID.lower()

    def _00x_to_xx00(des):
        convert_map = {"l": "al", "e": "ep", "c": "cp", "w":"wp", "a":"io", "b":"io", "s":"sh", "p":"sh"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[a-z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    nodeType = nodeType.upper()
    from datetime import datetime
    basinDate = datetime.now()
    basinmonth = basinDate.month
    basinYear = basinDate.year
    if btkID[:2] in ['sh', 'wp', 'io']:
        if btkID[:2] == 'sh':
            if basinmonth >= 7:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear+1}.dat'
            else:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
        else:
            btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
    else:
        btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'

    btk_data = fetch_url(btkUrl)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')

    cdx, cdy = [], []
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

    print(cdx, "\n", cdy)
    current_datetime = datetime.utcnow()

    def get_formatted_date(dt):
        year = str(dt.year)
        month = str(dt.month).zfill(2)
        day = str(dt.day).zfill(2)
        return year, month, day

    # Define the storm's coordinates
    storm_lat = float(cdy[-1])
    storm_lon = float(cdx[-1]) if float(cdx[-1]) > 0 else 360 + float(cdx[-1])

    # Calculate latitude and longitude bounds for the bounding box
    lat_min = storm_lat - 10
    lat_max = storm_lat + 10
    lon_min = storm_lon - 10
    lon_max = storm_lon + 10
    

    data_found = False
    retries = 0

    while not data_found and retries < 3:
        year, month, day = get_formatted_date(current_datetime)
        url = f'https://data.remss.com/smap/wind/L3/v01.0/daily/NRT/{year}/RSS_smap_wind_daily_{year}_{month}_{day}_NRT_v01.0.nc'
        destination = f'smap{year}{month}{day}.nc'
        print(f"Trying to download data for {year}-{month}-{day}")

        response = requests.get(url)
        with open(destination, 'wb') as file:
            file.write(response.content)

        # Open the NetCDF file using xarray
        ds = xr.open_dataset(destination, decode_times=False)

        # Extract the wind variable
        wind = ds['wind']

        # Extract wind data within the bounding box
        wind_bounded = wind.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

        # Check if wind data is available within the bounding box
        if not wind_bounded.isnull().all():
            data_found = True
        else:
            # If no data, remove the downloaded file and decrement the date by 1 day
            ds.close()
            os.remove(destination)
            current_datetime -= timedelta(days=1)
            retries += 1

    if not data_found:
        await ctx.send("No data available within the bounding box for the past day.")
        return

    await ctx.send("Generating data if available...")

    nodal = 0 if nodeType == 'ASC' else 1

    # Find the nearest latitude and longitude values in the dataset
    nearest_lat_index = np.abs(ds.lat.values - storm_lat).argmin()
    nearest_lon_index = np.abs(ds.lon.values - storm_lon).argmin()

    minute_data = ds.minute[nearest_lat_index, nearest_lon_index]
    print(minute_data)

    # Access the minute data for the nearest coordinate
    minute_data = ds.minute.isel(node=nodal).values[nearest_lat_index, nearest_lon_index]
    timePass = ""

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
    wind_bounded = wind_bounded.isel(node = nodal)
    max_wind_value = wind_bounded.max()

    # Create the plot
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Plot wind data using pcolormesh
    mesh = ax.pcolormesh(wind.lon, wind.lat, (wind.isel(node=nodal)) * 1.944, transform=ccrs.PlateCarree(), cmap='gist_ncar', vmin=0, vmax=150)
    contour_17 = ax.contour(wind.lon, wind.lat, wind.isel(node=nodal), levels=[17], colors='black', transform=ccrs.PlateCarree())
    contour_25 = ax.contour(wind.lon, wind.lat, wind.isel(node=nodal), levels=[25], colors='green', transform=ccrs.PlateCarree())
    contour_32 = ax.contour(wind.lon, wind.lat, wind.isel(node=nodal), levels=[32], colors='red', transform=ccrs.PlateCarree())

    # Add coastlines
    import cartopy.feature as cfeature
    from matplotlib import colors
    
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    

    # Add gridlines
    gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gls.top_labels = False  # suppress top labels
    gls.right_labels = False  # suppress right labels

    # Set the extent of the plot to zoom into the bounding box
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

    # Add title
    plt.title(f'SMAP SFC Winds\nTime: {timePass}, {year}/{month}/{day}', loc='left', fontsize=7)

    # Add colorbar
    cbar = plt.colorbar(mesh, ax=ax, shrink=0.5, extend='both')
    cbar.set_label('Wind Speed (kts)')
    # Print the maximum wind value within the bounding box
    max_wind_value = max_wind_value.values.item() * 1.944  # Get the raw value

    def oneMin(raw_SMAP):
        processed_SMAP = (362.644732816453 * raw_SMAP + 2913.62505913216) / 380.88384339523

        # Display output:
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
    await ctx.send("Here's the requested data.")

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)
    ds.close()
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
        import cartopy.feature as cfeature
        from matplotlib import colors
        
        ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
        ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
        ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))

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
async def pdoplot(ctx, year:int):
    import pandas as pd
    import matplotlib.pyplot as plt
    import os
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background")
    if year < 1854 or year > 2024:
        await ctx.send("Data is either not available or is currently yet to be created.")
        return

    # Load the PDO data from the text file
    file_path = 'pdo.txt' 
    df = pd.read_csv(file_path)
    # Filter data for the given year
    year_data = df[df['Year'] == year]

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot the data
    ax.plot(range(len(year_data.columns[1:])), year_data.values[0, 1:], marker='o', color='orange')

    # Annotate the values on the plot
    for i, txt in enumerate(year_data.values[0, 1:]):
        ax.annotate(f'{txt:.2f}', (i, txt), textcoords="offset points", xytext=(0, 5), ha='center')

    # Customize x-axis ticks
    ax.set_xticks(range(len(year_data.columns[1:])))
    ax.set_xticklabels(year_data.columns[1:])
    # Background color based on the sign of the values
    ax.axhspan(0, 1, facecolor='red', alpha=0.1)
    ax.axhspan(1, 2, facecolor='red', alpha=0.3)
    ax.axhspan(2, 3, facecolor='red', alpha=0.7)
    ax.axhspan(3, 4, facecolor='red', alpha=1)
    ax.axhspan(-1, 0, facecolor='blue', alpha=0.1)
    ax.axhspan(-2, -1, facecolor='blue', alpha=0.3)
    ax.axhspan(-3, -2, facecolor='blue', alpha=0.7)
    ax.axhspan(-4, -3, facecolor='blue', alpha=1)
    # Show the plot
    plt.title(f'PDO Data for {year} (1854-2024)')
    plt.xlabel('Months')
    plt.ylabel('PDO Values')
    plt.grid(True)
    plt.tight_layout()

    image_path = f'PDO_plot_for{year}.png'
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
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background")
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
    ax.axhspan(0, 0.5, facecolor='red', alpha=0.1)
    ax.axhspan(0.5, 1, facecolor='red', alpha=0.3)
    ax.axhspan(1, 1.5, facecolor='red', alpha=0.7)
    ax.axhspan(1.5, 3, facecolor='red', alpha=1)
    ax.axhspan(-0.5, 0, facecolor='blue', alpha=0.1)
    ax.axhspan(-1, -0.5, facecolor='blue', alpha=0.3)
    ax.axhspan(-1.5, -1, facecolor='blue', alpha=0.7)
    ax.axhspan(-3, -1.5, facecolor='blue', alpha=1)

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
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background")
    if year < 1871 or year > 2023:
        await ctx.send("Data is either not available or is currently yet to be created.")
        return

    # Load the MEIv2 data from the text file
    file_path = 'meiv2.txt' if year > 1978 else 'meiv2_old.txt'
    df = pd.read_csv(file_path)
    # Filter data for the given year
    year_data = df[df['Year'] == year]

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Plot the data
    ax.plot(range(len(year_data.columns[1:])), year_data.values[0, 1:], marker='o', color='orange')

    # Annotate the values on the plot
    for i, txt in enumerate(year_data.values[0, 1:]):
        ax.annotate(f'{txt:.2f}', (i, txt), textcoords="offset points", xytext=(0, 5), ha='center')

    # Customize x-axis ticks
    ax.set_xticks(range(len(year_data.columns[1:])))
    ax.set_xticklabels(year_data.columns[1:])
    # Background color based on the sign of the values
    ax.axhspan(0, 0.5, facecolor='red', alpha=0.1)
    ax.axhspan(0.5, 1, facecolor='red', alpha=0.3)
    ax.axhspan(1, 1.5, facecolor='red', alpha=0.7)
    ax.axhspan(1.5, 3, facecolor='red', alpha=1)
    ax.axhspan(-0.5, 0, facecolor='blue', alpha=0.1)
    ax.axhspan(-1, -0.5, facecolor='blue', alpha=0.3)
    ax.axhspan(-1.5, -1, facecolor='blue', alpha=0.7)
    ax.axhspan(-3, -1.5, facecolor='blue', alpha=1)
    # Show the plot
    plt.title(f'MEI Data for {year} (1871-2023)')
    plt.xlabel('Months (Two monthly averaged)')
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
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 

    def _00x_to_xx00(des):
        convert_map = {"L": "AL", "E": "EP", "C": "CP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[A-Z]$", btkID.upper()):    
        btkID = _00x_to_xx00(btkID.upper())

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    #http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")

    if btkID[:2].lower() in ['sh', 'wp', 'io']:
        btkUrl = f'https://www.emc.ncep.noaa.gov/gc_wmb/vxt/DECKS/b{btkID.lower()}{yr}.dat'
    else:
        btkUrl = f'https://www.emc.ncep.noaa.gov/gc_wmb/vxt/DECKS/b{btkID.lower()}{yr}.dat'

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
            if int(parameters[9].strip()) == 0:
                pres.append(1010)
            else:
                pres.append(int(parameters[9].strip()))
            r34.append(int(parameters[11].strip()))
            stormName = parameters[27].strip()

    #-------------------------------DEBUG INFORMATION-----------------------------------
    # print(cdx, "\n", cdy, "\n", winds, "\n", status, "\n", timeCheck, "\n", r34, "\n", DateTime)
    #-----------------------------------------------------------------------------------

    # Convert string datetime to datetime objects
    from datetime import datetime
    DateTimePlot = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in DateTime]

    # Create a figure and axis
    fig, ax1 = plt.subplots()

    # Plotting Winds on the primary Y-axis (left)
    ax1.set_xlabel('Date and Time')
    ax1.set_ylabel('Winds (Kts)', color='cyan')
    ax1.plot(DateTimePlot, winds, color='cyan')
    ax1.tick_params(axis='y', labelcolor='cyan')
    #plt.grid(True)
    if int(yr) > 2002:
        # Create a secondary Y-axis (right) for Pressure
        ax2 = ax1.twinx()
        ax2.set_ylabel('Pressure (hPa)', color='orange')
        ax2.plot(DateTimePlot, pres, color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')

    # Formatting date on the X-axis
    import matplotlib.dates as mdates
    import matplotlib.ticker as mticker

    def custom_date_formatter(x, pos=None):
        dt = mdates.num2date(x)
        # If it's January 1st at 00Z, show MM-DD and year
        if dt.month == 1 and dt.day == 1 and dt.hour == 0:
            return dt.strftime('%d\n%d\m%Y')
        # Otherwise, just show MM-DD
        elif dt.hour == 0:
            return dt.strftime('%d\n%m')
        return ''  # No label for other hours (12Z handled separately if needed)

    # --- X‑axis: 00Z labels only; 6‑hour gridlines ---
    # Major ticks at 00 UTC each day
    ax1.xaxis.set_major_locator(mdates.HourLocator(byhour=[0]))
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(custom_date_formatter))

    # Minor ticks at 06, 12, 18 UTC (so we don't double‑draw 00)
    ax1.xaxis.set_minor_locator(mdates.HourLocator(byhour=[6, 12, 18]))
    ax1.xaxis.set_minor_formatter(mticker.NullFormatter())  # no labels on minors

    # Smaller labels; no rotation
    ax1.tick_params(axis='x', which='major', labelsize=8, pad=2)
    ax1.tick_params(axis='x', which='minor', length=2)

    # Gridlines: stronger at 00Z (major), faint at 6‑hour minors
    ax1.grid(True, which='major', axis='x', linestyle='-', linewidth=0.8, alpha=0.7)
    ax1.grid(True, which='minor', axis='x', linestyle='--', linewidth=0.5, alpha=0.5)

    # Keep existing y‑grid if you like (your earlier plt.grid(True) did both axes);
    # If you've already called plt.grid(True) above and don't want double lines,
    # comment that out or limit to y only:
    ax1.grid(True, which='major', axis='y', alpha=0.7)

    # Make 00Z labels bold
    for lbl in ax1.get_xticklabels(which='major'):
        lbl.set_fontweight('bold')

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
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 

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

    def _00x_to_xx00(des):
        convert_map = {"L": "AL", "E": "EP", "C": "CP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[A-Z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    #Load in the loops for finding the latitude and longitude...
    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, winds, status, timeCheck, DateTime, pres = [], [], [], [], [], [], []
    storm_name = ""
    s_ID = ""
    vmax = -999
    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
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
    ax1.set_ylabel('Winds (Kts)', color='cyan')
    ax1.plot(DateTimePlot, winds, color='cyan')
    ax1.tick_params(axis='y', labelcolor='cyan')
    #plt.grid(True)
    if int(yr) > 2002:
        # Create a secondary Y-axis (right) for Pressure
        ax2 = ax1.twinx()
        ax2.set_ylabel('Pressure (hPa)', color='orange')
        ax2.plot(DateTimePlot, pres, color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')

    # Formatting date on the X-axis
    import matplotlib.dates as mdates
    import matplotlib.ticker as mticker

    def custom_date_formatter(x, pos=None):
        dt = mdates.num2date(x)
        # If it's January 1st at 00Z, show MM-DD and year
        if dt.month == 1 and dt.day == 1 and dt.hour == 0:
            return dt.strftime('%d\n%d\m%Y')
        # Otherwise, just show MM-DD
        elif dt.hour == 0:
            return dt.strftime('%d\n%m')
        return ''  # No label for other hours (12Z handled separately if needed)

    # --- X‑axis: 00Z labels only; 6‑hour gridlines ---
    # Major ticks at 00 UTC each day
    ax1.xaxis.set_major_locator(mdates.HourLocator(byhour=[0]))
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(custom_date_formatter))

    # Minor ticks at 06, 12, 18 UTC (so we don't double‑draw 00)
    ax1.xaxis.set_minor_locator(mdates.HourLocator(byhour=[6, 12, 18]))
    ax1.xaxis.set_minor_formatter(mticker.NullFormatter())  # no labels on minors

    # Smaller labels; no rotation
    ax1.tick_params(axis='x', which='major', labelsize=8, pad=2)
    ax1.tick_params(axis='x', which='minor', length=2)

    # Gridlines: stronger at 00Z (major), faint at 6‑hour minors
    ax1.grid(True, which='major', axis='x', linestyle='-', linewidth=0.8, alpha=0.7)
    ax1.grid(True, which='minor', axis='x', linestyle='--', linewidth=0.5, alpha=0.5)

    # Keep existing y‑grid if you like (your earlier plt.grid(True) did both axes);
    # If you've already called plt.grid(True) above and don't want double lines,
    # comment that out or limit to y only:
    ax1.grid(True, which='major', axis='y', alpha=0.7)

    # Make 00Z labels bold
    for lbl in ax1.get_xticklabels(which='major'):
        lbl.set_fontweight('bold')

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

    # Show the plot
    plt.title(f'{s_ID} {storm_name}', loc='center')
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
    if(btkID == 'UNNAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    print(f"Command received from server: {ctx.guild.name}")
    #Load in the loops for finding the latitude and longitude...
    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, winds, status, timeCheck, DateTime = [], [], [], [], [], []
    storm_name = ""
    s_ID = ""
    idl = False
    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
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
    import matplotlib.colors as mcolors
    import matplotlib.ticker as mticker
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
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

    from matplotlib import colors
    
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    if idl == False:
        ax.add_feature(cfeature.OCEAN, facecolor='#191919')

    if idl != True:
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

    '''
        if ratio < 0.3: 
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
        elif ratio > 0.7:
            ax.set_xlim(center_x-(center_height), center_x+(center_height))
            ax.set_ylim(center_y-center_height, center_y+center_height)
        else:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-center_height, center_y+center_height)
        '''
    #----NEW_H-----
    ax.set_xlim(minLong-8, maxLong+8)
    ax.set_ylim(minLat-2, maxLat+2)

    if idl == True:
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.xlocator = mticker.FixedLocator(range(-180, 181, 10))  # Control gridline spacing
        gl.ylocator = mticker.FixedLocator(range(-90, 91, 10))
        #gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
        gl.ylabel_style = {'size': 8, 'color': 'w'}
    
    #------------
    #Defining the legend box for the plot...
    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='Non-Tropical',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='Sub-Tropical',markerfacecolor='#444764', markersize=10),
    ]
    # Define the color mapping for wind speeds
    colors = ['b', 'g', '#ffff00', '#ffa001', '#ff5908', 'r', 'm']
    bounds = [0, 34, 64, 81, 96, 112, 137, 200]
    norm = mcolors.BoundaryNorm(bounds, len(colors))
    labels = ['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5']
    #------------
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

    plt.plot(LineX, LineY, color="#808080", linestyle="-")

    #Applying final touches...
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Peak Intensity: {vmax} Kts, {pmin} hPa', loc='left')
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right')
    ax.legend(handles=legend_elements, loc='best')
    plt.grid(True)
    #-----NEW-----------
    # Create the colorbar
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Add colorbar to the plot
    cbar = plt.colorbar(sm, ticks=bounds, orientation='horizontal', pad=0.05, aspect=50, ax=ax, shrink=0.5)
    cbar.set_label('SSHWS Windspeeds (Kts)')
    cbar.ax.set_xticklabels(['0', '34', '64', '81', '96', '112', '137', '200'])
    #---------------------
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
    import matplotlib.colors as mcolors
    import matplotlib.ticker as mticker
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
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

    from matplotlib import colors
    
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    if idl == False:
        ax.add_feature(cfeature.OCEAN, facecolor="#191919") 

    if idl != True:
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

    '''
        if ratio < 0.3: 
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-(center_width/2), center_y+(center_width/2))
        elif ratio > 0.7:
            ax.set_xlim(center_x-(center_height), center_x+(center_height))
            ax.set_ylim(center_y-center_height, center_y+center_height)
        else:
            ax.set_xlim(center_x-center_width, center_x+center_width)
            ax.set_ylim(center_y-center_height, center_y+center_height)
        '''
    #----NEW_H-----
    ax.set_xlim(minLong-8, maxLong+8)
    ax.set_ylim(minLat-2, maxLat+2)

    if idl == True:
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.xlocator = mticker.FixedLocator(range(-180, 181, 10))  # Control gridline spacing
        gl.ylocator = mticker.FixedLocator(range(-90, 91, 10))
        #gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
        gl.ylabel_style = {'size': 8, 'color': 'w'}
    
    #------------
    #Defining the legend box for the plot...
    legend_elements = [
                    Line2D([0], [0], marker='^', color='w', label='Non-Tropical',markerfacecolor='#444764', markersize=10),
                    Line2D([0], [0], marker='s', color='w', label='Sub-Tropical',markerfacecolor='#444764', markersize=10),
    ]
    # Define the color mapping for wind speeds
    colors = ['b', 'g', '#ffff00', '#ffa001', '#ff5908', 'r', 'm']
    bounds = [0, 34, 64, 81, 96, 112, 137, 200]
    norm = mcolors.BoundaryNorm(bounds, len(colors))
    labels = ['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5']
    #------------

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

    plt.plot(LineX, LineY, color="#808080", linestyle="-")

    #Applying final touches...
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Peak Intensity: {vmax} Kts, {pmin} hPa', loc='left')
    plt.title(f'ACE: {calc_ACE(winds, timeCheck)}', loc='right')
    ax.legend(handles=legend_elements, loc='upper left')
    plt.grid(True)
    #-----NEW-----------
    # Create the colorbar
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    ax.legend(handles=legend_elements, loc='best')

    # Add colorbar to the plot
    cbar = plt.colorbar(sm, ticks=bounds, orientation='horizontal', pad=0.05, aspect=50, ax=ax, shrink=0.5)
    cbar.set_label('SSHWS Windspeeds (Kts)')
    cbar.ax.set_xticklabels(['0', '34', '64', '81', '96', '112', '137', '200'])
    #---------------------
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

@bot.command(name='ascatplot_bt')
async def ascatplot_bt(ctx, satellite_search:str, btkID:str):
    import urllib3
    from bs4 import BeautifulSoup
    import datetime

    btkID = btkID.lower()
    def _00x_to_xx00(des):
        convert_map = {"l": "al", "e": "ep", "c": "cp", "w":"wp", "a":"io", "b":"io", "s":"sh", "p":"sh"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[a-z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    await ctx.send("Please wait. Due to my terrible potato laptop, the image may take a while to generate.")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    #http = urllib3.PoolManager(cert_reqs='CERT_NONE')

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    basinDate = datetime.datetime.now()
    basinmonth = basinDate.month
    basinYear = basinDate.year
    if btkID[:2] in ['sh', 'wp', 'io']:
        if btkID[:2] == 'sh':
            if basinmonth >= 7:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear+1}.dat'
            else:
                btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
        else:
            btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'
    else:
        btkUrl = f'https://www.natyphoon.top/atcf/temp/b{btkID}{basinYear}.dat'

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

    await ctx.send("Storm located, fetching data from EUMETSAT...")
    centerX, centerY = cdx[-1], cdy[-1]
    center_lat = cdy[-1] # Center latitude
    center_lon = cdx[-1] # Center longitude
    copyX = centerX + 360 if centerX < 0 else centerX
    DateTime = list(dict.fromkeys(DateTime))
    year, month, day, hour, minutes, seconds = map(int, DateTime[-1].replace('-', ' ').replace(':', ' ').split()) #Grab the latest values...

    from eumdac.token import AccessToken
    from eumdac.datastore import DataStore
    import shutil
    import zipfile
    import os
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import matplotlib.colors as mcolors
    import glob
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 

    satellite_search = satellite_search.lower()
    await ctx.send("Searching for files...")

    consumer_key = 'CONSUMER_KEY'
    consumer_secret = 'CONSUMER_SECRET'

    credentials = (consumer_key, consumer_secret)
    token = AccessToken(credentials)
    datastore = DataStore(token)

    selected_collection = datastore.get_collection('EO:EUM:DAT:METOP:OAS025')

    # Set sensing start and end time
    end = datetime.datetime(year, month, day, hour, 0)
    start = end - datetime.timedelta(hours=6)

    selected_products = selected_collection.search(dtstart = start, dtend = end)

    print(f'Found Datasets: {selected_products.total_results} datasets for the given time range')
    if selected_products.total_results > 0:
        await ctx.send("Datasets found, initiating download...")
    else:
        await ctx.send("None found, aborting process.")
    for product in selected_products:
        product_name = str(product)  # Convert the product object to a string to get the filename
        # Filter by satellite type
        if satellite_search in product_name:
            print(f"Downloading: {product_name}")
            try:
                with product.open() as fsrc, \
                    open(fsrc.name, mode='wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst)
                print(f"Downloaded {fdst.name}")
            except Exception as e:
                print(f"Failed to download {product}: {e}") # Print the product object for better context on error
        else:
            print(f"Skipping {product_name} as it is not a {satellite_search.upper()} product.")

    print("Download process complete.")

    #Extract the downloaded zip files
    # Get a list of all files in the current directory
    all_files = os.listdir('.')

    # Filter for zip files
    zip_files = [f for f in all_files if f.endswith('.zip')]

    print(f"Found {len(zip_files)} zip files to extract.")

    for zip_file in zip_files:
        print(f"Extracting: {zip_file}")
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall('.') # Extract to the current directory
            print(f"Successfully extracted: {zip_file}")
        except zipfile.BadZipFile:
            print(f"Error: {zip_file} is not a valid zip file.")
        except Exception as e:
            print(f"Error extracting {zip_file}: {e}")

    print("Extraction process complete.")

    await ctx.send("Plotting data. Please wait, this may take some time.")

    # Step 5: Open NetCDF files using xarray
    import xarray as xr
    import os

    # Get a list of all files in the current directory
    all_files = os.listdir('.')

    # Filter for NetCDF files that start with 'ascat_' and end with '.nc'
    netcdf_files = [f for f in all_files if (f.startswith('ascat_') or f.startswith('OASW')) and f.endswith('.nc')]

    print(f"Found {len(netcdf_files)} NetCDF files to open.")

    # Dictionary to store opened datasets
    datasets = {}

    for nc_file in netcdf_files:
        print(f"Opening: {nc_file}")
        try:
            ds = xr.open_dataset(nc_file)
            datasets[nc_file] = ds
            print(f"Successfully opened: {nc_file}")
        except Exception as e:
            print(f"Error opening {nc_file}: {e}")

    print("All specified NetCDF files have been processed.")

    min_lat = center_lat-5
    max_lat = center_lat+5
    min_lon = center_lon-5
    max_lon = center_lon+5

    # Calculate the center latitude and longitude for the plot
    plot_center_lat = (min_lat + max_lat) / 2
    plot_center_lon = (min_lon + max_lon) / 2
    plot_center_lon = plot_center_lon + 360 if plot_center_lon < 0 else plot_center_lon
    print(f"Plot Center Latitude: {plot_center_lat}")
    print(f"Plot Center Longitude: {plot_center_lon}")

    import numpy as np

    # Initialize variables to store the minimum distance and nearest pixel information
    min_distance = float('inf')
    nearest_pixel_info = None
    max_wind = 0
    for filename, ds in datasets.items():
        try:
            lat_values = ds['lat'].values
            lon_values = ds['lon'].values
            wind_speed_values = ds['wind_speed'].values * 1.94384
            for row_index in range(lat_values.shape[0]):
                for col_index in range(lat_values.shape[1]):
                    pixel_lat = lat_values[row_index, col_index]
                    pixel_lon = lon_values[row_index, col_index]
                    distance = np.sqrt((pixel_lat - plot_center_lat)**2 + (pixel_lon - plot_center_lon)**2)
                    if distance <= 5:
                        max_wind = max(max_wind, wind_speed_values[row_index, col_index])
                    if distance < min_distance:
                        min_distance = distance
                        nearest_pixel_info = (filename, (row_index, col_index))

        except KeyError as e:
            print(f"Error: Variable {e} not found in dataset {filename}")
        except Exception as e:
            print(f"Error processing dataset {filename}: {e}")

    max_wind_converted = ((0.014 * (max_wind/1.94384) ** 2) + (0.821 * (max_wind/1.94384)) + 0.961) * 1.94384

    if nearest_pixel_info:
        print(f"The nearest pixel to the plot center is in file: {nearest_pixel_info[0]} at index: {nearest_pixel_info[1]}")
        print(f"Minimum distance: {min_distance}")
        if min_distance > 5:
            await ctx.send("The nearest pixel to the plot center is more than 5 degrees away from the plot center. Please try again later.")
            
            # Close all opened datasets
            for filename, ds in datasets.items():
                try:
                    ds.close()
                    print(f"Closed dataset: {filename}")
                except Exception as e:
                    print(f"Error closing dataset {filename}: {e}")

            print("All datasets have been closed.")

            # Find all files starting with 'ascat_'
            files_to_delete = glob.glob('ascat_*')
            add_to_delete = glob.glob('*.xml')
            files_to_delete.extend(add_to_delete)
            add_to_delete = glob.glob('OASW*')
            files_to_delete.extend(add_to_delete)

            print(f"Found {len(files_to_delete)} files to delete.")

            # Delete each file
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")
            print("Deletion process complete.")
            
            return
    else:
        print("No nearest pixel found. There might be an issue with the datasets or variables.")
    # Access the dataset using the filename from nearest_pixel_info
    nearest_dataset_name = nearest_pixel_info[0]
    nearest_ds = datasets[nearest_dataset_name]

    # Extract the 'time' variable from the selected dataset
    nearest_pixel_time = nearest_ds['time'].values
    #print(f"Time at the nearest pixel: {nearest_pixel_time}")
    # Extract the index of the nearest pixel
    row_index, col_index = nearest_pixel_info[1]
    # Extract the single time value at the nearest pixel's index
    nearest_pixel_time_value = nearest_ds['time'].values[row_index, col_index]

    print(f"Single time value at the nearest pixel: {nearest_pixel_time_value}")

    import pandas as pd

    # Convert the nearest_pixel_time_value to a pandas Timestamp object
    nearest_pixel_timestamp = pd.Timestamp(nearest_pixel_time_value)

    # Format the pandas Timestamp object into a string
    formatted_time_string = nearest_pixel_timestamp.strftime('%Y-%m-%d %H:%M')

    # Print the formatted time string to verify the result
    print(f"Formatted time string: {formatted_time_string}")

    # Create a figure and axes with a PlateCarree projection
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add coastlines and countries
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)

    # Add gridlines for reference
    gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False  # Turn off top labels
    gl.right_labels = False # Turn off right labels

    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    # Define color levels for wind speed
    wind_speed_levels = np.arange(0, 80, 5)  # 0 to 75 in increments of 5

    # Define custom colormap
    colors = ['blue', 'green', 'yellow', 'red', 'purple', 'brown', 'pink']
    cmap_name = 'ascat_cmap'
    cm = mcolors.LinearSegmentedColormap.from_list(cmap_name, colors, N=len(wind_speed_levels)-1)

    norm = mcolors.BoundaryNorm(wind_speed_levels, cm.N)

    # Iterate through the opened datasets
    for filename, ds in datasets.items():
        try:
            wind_speed = ds['wind_speed'] * 1.94384 #Convert to knots
            wind_dir = ds['wind_dir']
            lon = ds['lon']
            lat = ds['lat']

            # Convert wind direction from degrees to radians
            wind_dir_rad = np.deg2rad(wind_dir)

            # Calculate U and V components
            u_full = wind_speed * np.sin(wind_dir_rad)
            v_full = wind_speed * np.cos(wind_dir_rad)

            # Check if the dataset's spatial extent is within the desired bounds
            # Colorcode the barbs based on wind speed
            cs = ax.barbs(lon[:], lat[:], u_full.values, v_full.values, wind_speed.values,
                        cmap=cm, norm=norm, length=5) # Use custom colormap

        except KeyError as e:
            print(f"Error: Variable {e} not found in dataset {filename}")
        except Exception as e:
            print(f"Error processing dataset {filename}: {e}")

    # Create the plot title with the wind information and the time of the nearest pixel
    #{s_ID} {storm_name}
    title_string = f'ASCAT 25km Winds for {btkID.upper()} {stormName} | {satellite_search.upper()} | {formatted_time_string} UTC\nMax wind (unconverted) = {max_wind:.02f} kts | Max wind (converted) = {max_wind_converted:.02f} kts'

    ax.set_title(title_string)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Add a colorbar
    cbar = fig.colorbar(cs, ticks=wind_speed_levels)
    cbar.set_label('Wind Speed (knots)')

    plt.tight_layout()
    import random
    image_path = f'ascat_nc{random.randint(1, 100)}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)

    # Close all opened datasets
    for filename, ds in datasets.items():
        try:
            ds.close()
            print(f"Closed dataset: {filename}")
        except Exception as e:
            print(f"Error closing dataset {filename}: {e}")

    print("All datasets have been closed.")

    # Find all files starting with 'ascat_'
    files_to_delete = glob.glob('ascat_*')
    add_to_delete = glob.glob('*.xml')
    files_to_delete.extend(add_to_delete)
    add_to_delete = glob.glob('OASW*')
    files_to_delete.extend(add_to_delete)

    print(f"Found {len(files_to_delete)} files to delete.")

    # Delete each file
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")
    print("Deletion process complete.")

@bot.command(name='ascatplot_tc')
async def ascatplot_tc(ctx, satellite_search:str, btkID:str, yr, hour:int, date:str):
    import datetime
    from eumdac.token import AccessToken
    from eumdac.datastore import DataStore
    import shutil
    import zipfile
    import os
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import matplotlib.colors as mcolors
    import glob
    import matplotlib.style as mplstyle
    mplstyle.use("dark_background") 
    import csv

    satellite_search = satellite_search.lower()
    day, month, year = int(date.split('/')[0]), int(date.split('/')[1]), int(date.split('/')[2])

    btkID = btkID.upper()

    if btkID == 'BENTO':
        btkID = 'BENTOJANA'
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'VICKY 2020', 'JOYCE 2018', 'GORDON 1979', 'BENI 2003', 'MARK 1992', 'NADINE 1978',
                  'WINNIE 1978', 'HARVEY 2005', 'FREDA 1981', 'POLLY 1971', 'LOUISE 1970', 'LUCY 1962', 'CARMEN 1974']
    
    check = f"{btkID} {yr}"
    
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    if(btkID == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    if(btkID == 'UNNAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    
    def _00x_to_xx00(des):
        convert_map = {"L": "AL", "E": "EP", "C": "CP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[A-Z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    #Load in the loops for finding the latitude and longitude...

    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, DateTime = 0, 0, ""
    storm_name = ""
    s_ID = ""
    idl = False
    basin = ''
    hx = int(hour)
    await ctx.send("Please wait. Due to my terrible potato laptop, the dataset may take a while to go through.")

    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]):
                    DateTime = lines[6]
                    basin = lines[3]
                    if int(DateTime[:4]) == year and int(DateTime[5:7]) == month and int(DateTime[8:10]) == day and int(DateTime[-8:-6]) == hx:
                        s_ID = lines[18]
                        cdy, cdx = float(lines[19]), float(lines[20])
                        if(float(cdx) <= -173.5 or float(cdx) >= 173.5):
                            idl = True
                        storm_name = lines[5]
                        break
    
    if cdx == 0:
        await ctx.send("Error 404: Storm not found. Please check if your entry is correct.")
        return

    await ctx.send("System located in database, fetching appropriate satellite...")

    center_lat = cdy # Center latitude
    center_lon = cdx # Center longitude

    await ctx.send("Searching for files...")

    consumer_key = 'CONSUMER_KEY'
    consumer_secret = 'CONSUMER_SECRET'

    credentials = (consumer_key, consumer_secret)
    token = AccessToken(credentials)
    datastore = DataStore(token)

    selected_collection = datastore.get_collection('EO:EUM:DAT:METOP:OAS025')

    # Set sensing start and end time
    end = datetime.datetime(year, month, day, hour, 0)
    start = end - datetime.timedelta(hours=6)

    selected_products = selected_collection.search(dtstart = start, dtend = end)

    print(f'Found Datasets: {selected_products.total_results} datasets for the given time range')
    if selected_products.total_results > 0:
        await ctx.send("Datasets found, initiating download...")
    else:
        await ctx.send("None found, aborting process.")
    for product in selected_products:
        product_name = str(product)  # Convert the product object to a string to get the filename
        # Filter by satellite type
        if satellite_search in product_name:
            print(f"Downloading: {product_name}")
            try:
                with product.open() as fsrc, \
                    open(fsrc.name, mode='wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst)
                print(f"Downloaded {fdst.name}")
            except Exception as e:
                print(f"Failed to download {product}: {e}") # Print the product object for better context on error
        else:
            print(f"Skipping {product_name} as it is not a {satellite_search.upper()} product.")

    print("Download process complete.")

    #Extract the downloaded zip files
    # Get a list of all files in the current directory
    all_files = os.listdir('.')

    # Filter for zip files
    zip_files = [f for f in all_files if f.endswith('.zip')]

    print(f"Found {len(zip_files)} zip files to extract.")

    for zip_file in zip_files:
        print(f"Extracting: {zip_file}")
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall('.') # Extract to the current directory
            print(f"Successfully extracted: {zip_file}")
        except zipfile.BadZipFile:
            print(f"Error: {zip_file} is not a valid zip file.")
        except Exception as e:
            print(f"Error extracting {zip_file}: {e}")

    print("Extraction process complete.")

    await ctx.send("Plotting data. Please wait, this may take some time.")

    # Step 5: Open NetCDF files using xarray
    import xarray as xr
    import os

    # Get a list of all files in the current directory
    all_files = os.listdir('.')

    # Filter for NetCDF files that start with 'ascat_' and end with '.nc'
    netcdf_files = [f for f in all_files if (f.startswith('ascat_') or f.startswith('OASW')) and f.endswith('.nc')]

    print(f"Found {len(netcdf_files)} NetCDF files to open.")

    # Dictionary to store opened datasets
    datasets = {}

    for nc_file in netcdf_files:
        print(f"Opening: {nc_file}")
        try:
            ds = xr.open_dataset(nc_file)
            datasets[nc_file] = ds
            print(f"Successfully opened: {nc_file}")
        except Exception as e:
            print(f"Error opening {nc_file}: {e}")

    print("All specified NetCDF files have been processed.")

    center_lat, center_lon = cdy, cdx

    min_lat = center_lat-5
    max_lat = center_lat+5
    min_lon = center_lon-5
    max_lon = center_lon+5

    # Calculate the center latitude and longitude for the plot
    plot_center_lat = (min_lat + max_lat) / 2
    plot_center_lon = (min_lon + max_lon) / 2
    plot_center_lon = plot_center_lon + 360 if plot_center_lon < 0 else plot_center_lon
    print(f"Plot Center Latitude: {plot_center_lat}")
    print(f"Plot Center Longitude: {plot_center_lon}")

    import numpy as np

    # Initialize variables to store the minimum distance and nearest pixel information
    min_distance = float('inf')
    nearest_pixel_info = None
    max_wind = 0
    for filename, ds in datasets.items():
        try:
            lat_values = ds['lat'].values
            lon_values = ds['lon'].values
            wind_speed_values = ds['wind_speed'].values * 1.94384
            for row_index in range(lat_values.shape[0]):
                for col_index in range(lat_values.shape[1]):
                    pixel_lat = lat_values[row_index, col_index]
                    pixel_lon = lon_values[row_index, col_index]
                    distance = np.sqrt((pixel_lat - plot_center_lat)**2 + (pixel_lon - plot_center_lon)**2)
                    if distance <= 5:
                        max_wind = max(max_wind, wind_speed_values[row_index, col_index])
                    if distance < min_distance:
                        min_distance = distance
                        nearest_pixel_info = (filename, (row_index, col_index))

        except KeyError as e:
            print(f"Error: Variable {e} not found in dataset {filename}")
        except Exception as e:
            print(f"Error processing dataset {filename}: {e}")

    max_wind_converted = ((0.014 * (max_wind/1.94384) ** 2) + (0.821 * (max_wind/1.94384)) + 0.961) * 1.94384

    if nearest_pixel_info:
        print(f"The nearest pixel to the plot center is in file: {nearest_pixel_info[0]} at index: {nearest_pixel_info[1]}")
        print(f"Minimum distance: {min_distance}")
        if min_distance > 5:
            await ctx.send("The nearest pixel to the plot center is more than 5 degrees away from the plot center. Please try again later.")
            
            # Close all opened datasets
            for filename, ds in datasets.items():
                try:
                    ds.close()
                    print(f"Closed dataset: {filename}")
                except Exception as e:
                    print(f"Error closing dataset {filename}: {e}")

            print("All datasets have been closed.")

            # Find all files starting with 'ascat_'
            files_to_delete = glob.glob('ascat_*')
            add_to_delete = glob.glob('*.xml')
            files_to_delete.extend(add_to_delete)
            add_to_delete = glob.glob('OASW*')
            files_to_delete.extend(add_to_delete)

            print(f"Found {len(files_to_delete)} files to delete.")

            # Delete each file
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")
            print("Deletion process complete.")
            
            return
    else:
        print("No nearest pixel found. There might be an issue with the datasets or variables.")
    # Access the dataset using the filename from nearest_pixel_info
    nearest_dataset_name = nearest_pixel_info[0]
    nearest_ds = datasets[nearest_dataset_name]

    # Extract the 'time' variable from the selected dataset
    nearest_pixel_time = nearest_ds['time'].values
    #print(f"Time at the nearest pixel: {nearest_pixel_time}")
    # Extract the index of the nearest pixel
    row_index, col_index = nearest_pixel_info[1]
    # Extract the single time value at the nearest pixel's index
    nearest_pixel_time_value = nearest_ds['time'].values[row_index, col_index]

    print(f"Single time value at the nearest pixel: {nearest_pixel_time_value}")

    import pandas as pd

    # Convert the nearest_pixel_time_value to a pandas Timestamp object
    nearest_pixel_timestamp = pd.Timestamp(nearest_pixel_time_value)

    # Format the pandas Timestamp object into a string
    formatted_time_string = nearest_pixel_timestamp.strftime('%Y-%m-%d %H:%M')

    # Print the formatted time string to verify the result
    print(f"Formatted time string: {formatted_time_string}")

    # Create a figure and axes with a PlateCarree projection
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add coastlines and countries
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)

    # Add gridlines for reference
    gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False  # Turn off top labels
    gl.right_labels = False # Turn off right labels

    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    # Define color levels for wind speed
    wind_speed_levels = np.arange(0, 80, 5)  # 0 to 75 in increments of 5

    # Define custom colormap
    colors = ['blue', 'green', 'yellow', 'red', 'purple', 'brown', 'pink']
    cmap_name = 'ascat_cmap'
    cm = mcolors.LinearSegmentedColormap.from_list(cmap_name, colors, N=len(wind_speed_levels)-1)

    norm = mcolors.BoundaryNorm(wind_speed_levels, cm.N)

    # Iterate through the opened datasets
    for filename, ds in datasets.items():
        try:
            wind_speed = ds['wind_speed'] * 1.94384 #Convert to knots
            wind_dir = ds['wind_dir']
            lon = ds['lon']
            lat = ds['lat']

            # Convert wind direction from degrees to radians
            wind_dir_rad = np.deg2rad(wind_dir)

            # Calculate U and V components
            u_full = wind_speed * np.sin(wind_dir_rad)
            v_full = wind_speed * np.cos(wind_dir_rad)

            # Check if the dataset's spatial extent is within the desired bounds
            # Colorcode the barbs based on wind speed
            cs = ax.barbs(lon[:], lat[:], u_full.values, v_full.values, wind_speed.values,
                        cmap=cm, norm=norm, length=5) # Use custom colormap

        except KeyError as e:
            print(f"Error: Variable {e} not found in dataset {filename}")
        except Exception as e:
            print(f"Error processing dataset {filename}: {e}")

    # Create the plot title with the wind information and the time of the nearest pixel
    #{s_ID} {storm_name}
    title_string = f'ASCAT 25km Winds for {s_ID} {storm_name} | {satellite_search.upper()} | {formatted_time_string} UTC\nMax wind (unconverted) = {max_wind:.02f} kts | Max wind (converted) = {max_wind_converted:.02f} kts'

    ax.set_title(title_string)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Add a colorbar
    cbar = fig.colorbar(cs, ticks=wind_speed_levels)
    cbar.set_label('Wind Speed (knots)')

    plt.tight_layout()
    import random
    image_path = f'ascat_nc{random.randint(1, 100)}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)

    # Close all opened datasets
    for filename, ds in datasets.items():
        try:
            ds.close()
            print(f"Closed dataset: {filename}")
        except Exception as e:
            print(f"Error closing dataset {filename}: {e}")

    print("All datasets have been closed.")

    # Find all files starting with 'ascat_'
    files_to_delete = glob.glob('ascat_*')
    add_to_delete = glob.glob('*.xml')
    files_to_delete.extend(add_to_delete)
    add_to_delete = glob.glob('OASW*')
    files_to_delete.extend(add_to_delete)

    print(f"Found {len(files_to_delete)} files to delete.")

    # Delete each file
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")
    print("Deletion process complete.")

@bot.command(name='ascatplot')
async def ascatplot(ctx, satellite_search:str, lat:float, lon:float, hour:int, date:str):
    import datetime
    from eumdac.token import AccessToken
    from eumdac.datastore import DataStore
    import shutil
    import zipfile
    import os
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import matplotlib.colors as mcolors
    import glob
    import matplotlib.style as mplstyle
    mplstyle.use("dark_background") 
    satellite_search = satellite_search.lower()
    await ctx.send("Searching for files...")

    consumer_key = 'CONSUMER_KEY'
    consumer_secret = 'CONSUMER_SECRET'

    credentials = (consumer_key, consumer_secret)
    token = AccessToken(credentials)
    datastore = DataStore(token)

    selected_collection = datastore.get_collection('EO:EUM:DAT:METOP:OAS025')
    day, month, year = int(date.split('/')[0]), int(date.split('/')[1]), int(date.split('/')[2])

    # Set sensing start and end time
    end = datetime.datetime(year, month, day, hour, 0)
    start = end - datetime.timedelta(hours=6)

    selected_products = selected_collection.search(dtstart = start, dtend = end)

    print(f'Found Datasets: {selected_products.total_results} datasets for the given time range')
    if selected_products.total_results > 0:
        await ctx.send("Datasets found, initiating download...")
    else:
        await ctx.send("None found, aborting process.")
    for product in selected_products:
        product_name = str(product)  # Convert the product object to a string to get the filename
        # Filter by satellite type
        if satellite_search in product_name:
            print(f"Downloading: {product_name}")
            try:
                with product.open() as fsrc, \
                    open(fsrc.name, mode='wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst)
                print(f"Downloaded {fdst.name}")
            except Exception as e:
                print(f"Failed to download {product}: {e}") # Print the product object for better context on error
        else:
            print(f"Skipping {product_name} as it is not a {satellite_search.upper()} product.")

    print("Download process complete.")

    #Extract the downloaded zip files
    # Get a list of all files in the current directory
    all_files = os.listdir('.')

    # Filter for zip files
    zip_files = [f for f in all_files if f.endswith('.zip')]

    print(f"Found {len(zip_files)} zip files to extract.")

    for zip_file in zip_files:
        print(f"Extracting: {zip_file}")
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall('.') # Extract to the current directory
            print(f"Successfully extracted: {zip_file}")
        except zipfile.BadZipFile:
            print(f"Error: {zip_file} is not a valid zip file.")
        except Exception as e:
            print(f"Error extracting {zip_file}: {e}")

    print("Extraction process complete.")

    await ctx.send("Plotting data. Please wait, this may take some time.")

    # Step 5: Open NetCDF files using xarray
    import xarray as xr
    import os

    # Get a list of all files in the current directory
    all_files = os.listdir('.')

    # Filter for NetCDF files that start with 'ascat_' and end with '.nc'
    netcdf_files = [f for f in all_files if (f.startswith('ascat_') or f.startswith('OASW')) and f.endswith('.nc')]

    print(f"Found {len(netcdf_files)} NetCDF files to open.")

    # Dictionary to store opened datasets
    datasets = {}

    for nc_file in netcdf_files:
        print(f"Opening: {nc_file}")
        try:
            ds = xr.open_dataset(nc_file)
            datasets[nc_file] = ds
            print(f"Successfully opened: {nc_file}")
        except Exception as e:
            print(f"Error opening {nc_file}: {e}")

    print("All specified NetCDF files have been processed.")

    center_lat, center_lon = lat, lon

    min_lat = center_lat-5
    max_lat = center_lat+5
    min_lon = center_lon-5
    max_lon = center_lon+5

    # Calculate the center latitude and longitude for the plot
    plot_center_lat = (min_lat + max_lat) / 2
    plot_center_lon = (min_lon + max_lon) / 2
    plot_center_lon = plot_center_lon + 360 if plot_center_lon < 0 else plot_center_lon
    print(f"Plot Center Latitude: {plot_center_lat}")
    print(f"Plot Center Longitude: {plot_center_lon}")

    import numpy as np

    # Initialize variables to store the minimum distance and nearest pixel information
    min_distance = float('inf')
    nearest_pixel_info = None
    max_wind = 0
    for filename, ds in datasets.items():
        try:
            lat_values = ds['lat'].values
            lon_values = ds['lon'].values
            wind_speed_values = ds['wind_speed'].values * 1.94384
            for row_index in range(lat_values.shape[0]):
                for col_index in range(lat_values.shape[1]):
                    pixel_lat = lat_values[row_index, col_index]
                    pixel_lon = lon_values[row_index, col_index]
                    distance = np.sqrt((pixel_lat - plot_center_lat)**2 + (pixel_lon - plot_center_lon)**2)
                    if distance <= 5:
                        if max_wind < wind_speed_values[row_index, col_index]:
                            max_wind = wind_speed_values[row_index, col_index]
                    if distance < min_distance:
                        min_distance = distance
                        nearest_pixel_info = (filename, (row_index, col_index))

        except KeyError as e:
            print(f"Error: Variable {e} not found in dataset {filename}")
        except Exception as e:
            print(f"Error processing dataset {filename}: {e}")

    max_wind_converted = ((0.014 * (max_wind/1.94384) ** 2) + (0.821 * (max_wind/1.94384)) + 0.961) * 1.94384

    if nearest_pixel_info:
        print(f"The nearest pixel to the plot center is in file: {nearest_pixel_info[0]} at index: {nearest_pixel_info[1]}")
        print(f"Minimum distance: {min_distance}")
        if min_distance > 5:
            await ctx.send("The nearest pixel to the plot center is more than 5 degrees away from the plot center. Please try again later.")
            
            # Close all opened datasets
            for filename, ds in datasets.items():
                try:
                    ds.close()
                    print(f"Closed dataset: {filename}")
                except Exception as e:
                    print(f"Error closing dataset {filename}: {e}")

            print("All datasets have been closed.")

            # Find all files starting with 'ascat_'
            files_to_delete = glob.glob('ascat_*')
            add_to_delete = glob.glob('*.xml')
            files_to_delete.extend(add_to_delete)
            add_to_delete = glob.glob('OASW*')
            files_to_delete.extend(add_to_delete)

            print(f"Found {len(files_to_delete)} files to delete.")

            # Delete each file
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")
            print("Deletion process complete.")
            return
    else:
        print("No nearest pixel found. There might be an issue with the datasets or variables.")

    # Access the dataset using the filename from nearest_pixel_info
    nearest_dataset_name = nearest_pixel_info[0]
    nearest_ds = datasets[nearest_dataset_name]

    # Extract the 'time' variable from the selected dataset
    nearest_pixel_time = nearest_ds['time'].values
    #print(f"Time at the nearest pixel: {nearest_pixel_time}")
    # Extract the index of the nearest pixel
    row_index, col_index = nearest_pixel_info[1]
    # Extract the single time value at the nearest pixel's index
    nearest_pixel_time_value = nearest_ds['time'].values[row_index, col_index]

    print(f"Single time value at the nearest pixel: {nearest_pixel_time_value}")

    import pandas as pd

    # Convert the nearest_pixel_time_value to a pandas Timestamp object
    nearest_pixel_timestamp = pd.Timestamp(nearest_pixel_time_value)

    # Format the pandas Timestamp object into a string
    formatted_time_string = nearest_pixel_timestamp.strftime('%Y-%m-%d %H:%M')

    # Print the formatted time string to verify the result
    print(f"Formatted time string: {formatted_time_string}")

    # Create a figure and axes with a PlateCarree projection
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add coastlines and countries
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)

    # Add gridlines for reference
    gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False  # Turn off top labels
    gl.right_labels = False # Turn off right labels

    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    # Define color levels for wind speed
    wind_speed_levels = np.arange(0, 80, 5)  # 0 to 75 in increments of 5

    # Define custom colormap
    colors = ['blue', 'green', 'yellow', 'red', 'purple', 'brown', 'pink']
    cmap_name = 'ascat_cmap'
    cm = mcolors.LinearSegmentedColormap.from_list(cmap_name, colors, N=len(wind_speed_levels)-1)

    norm = mcolors.BoundaryNorm(wind_speed_levels, cm.N)

    # Iterate through the opened datasets
    for filename, ds in datasets.items():
        try:
            wind_speed = ds['wind_speed'] * 1.94384 #Convert to knots
            wind_dir = ds['wind_dir']
            lon = ds['lon']
            lat = ds['lat']

            # Convert wind direction from degrees to radians
            wind_dir_rad = np.deg2rad(wind_dir)

            # Calculate U and V components
            u_full = wind_speed * np.sin(wind_dir_rad)
            v_full = wind_speed * np.cos(wind_dir_rad)

            # Check if the dataset's spatial extent is within the desired bounds
            # Colorcode the barbs based on wind speed
            cs = ax.barbs(lon[:], lat[:], u_full.values, v_full.values, wind_speed.values,
                        cmap=cm, norm=norm, length=5) # Use custom colormap

        except KeyError as e:
            print(f"Error: Variable {e} not found in dataset {filename}")
        except Exception as e:
            print(f"Error processing dataset {filename}: {e}")

    # Create the plot title with the wind information and the time of the nearest pixel
    title_string = f'ASCAT 25km Winds ({center_lat}, {center_lon}) | {satellite_search.upper()} | {formatted_time_string} UTC\nMax wind (unconverted) = {max_wind:.02f} kts | Max wind (converted) = {max_wind_converted:.02f} kts'

    ax.set_title(title_string)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Add a colorbar
    cbar = fig.colorbar(cs, ticks=wind_speed_levels)
    cbar.set_label('Wind Speed (knots)')

    plt.tight_layout()
    import random
    image_path = f'ascat_nc{random.randint(1, 100)}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)

    # Close all opened datasets
    for filename, ds in datasets.items():
        try:
            ds.close()
            print(f"Closed dataset: {filename}")
        except Exception as e:
            print(f"Error closing dataset {filename}: {e}")

    print("All datasets have been closed.")

    # Find all files starting with 'ascat_'
    files_to_delete = glob.glob('ascat_*')
    add_to_delete = glob.glob('*.xml')
    files_to_delete.extend(add_to_delete)
    add_to_delete = glob.glob('OASW*')
    files_to_delete.extend(add_to_delete)

    print(f"Found {len(files_to_delete)} files to delete.")

    # Delete each file
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")
    print("Deletion process complete.")

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
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
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

@bot.command(name='jwt')
async def jwt(ctx, rmw_nm:float, windspeed:float):
    import matplotlib.pyplot as plt
    import matplotlib.style as mplstyle
    import numpy as np
    import os
    mplstyle.use("dark_background") 

    rmw_km = rmw_nm * 1.852
    def rmw_curve_ratio(fl_rmw):
        a, b, c = 1.159321, -0.097488, 0.006063
        R = np.asarray(fl_rmw, dtype=float)
        t = np.log(R)
        return  (a + b*t + c*t**2) * (0.9/0.885)
    
    ratio = rmw_curve_ratio(rmw_km)
    windspeed_converted = windspeed * ratio
    ratio = "{:.2f}".format(ratio)

    R_values = np.linspace(1, max(100, rmw_km+5), 200)
    y_values = rmw_curve_ratio(R_values)

    plt.plot(R_values, y_values)

    windspeed_converted = "{:.2f} kts".format(windspeed_converted)

    # Add the x = ratio line
    x_values = np.array([rmw_km, rmw_km])  # create an array with two identical values
    y_values = np.array([0.8, 1.8])  # create an array with two values that span the y-axis
    plt.plot(x_values, y_values, 'r--', label=f'FL-derived RMW = {rmw_nm:.2f} nm / {rmw_km:.2f} km\n700mb reduced Ratio (JWT et al. 2030+): {ratio}\nOriginal / Reduced Windspeed = {windspeed:.2f} kts / {windspeed_converted}')  # plot the line with a red dashed style
    plt.xlim(0, max(100, rmw_km+5))  # set x-axis range to 0-100
    plt.ylim(0.8, 1.2)  # set y-axis range to 
    plt.xlabel("RMW (km)")
    plt.ylabel("FL Reduction Ratio")
    plt.grid(True)
    plt.title("A log regression for JWT's new FL reduction Ratios")
    plt.legend()
    import random
    plt.tight_layout()
    image_path = f'jwt{random.randint(1, 100)}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)

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

@bot.command('mcfetch_nc')
async def mcfetch_nc(ctx, btkID, yr, hour, date, col:str):
    import matplotlib.style as mplstyle
    import cmap_collection
    import csv
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import requests
    import os
    from io import BytesIO
    from matplotlib.colors import ListedColormap, LinearSegmentedColormap
    import matplotlib.ticker as mticker
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    from datetime import datetime
    mplstyle.use("dark_background") 
    
    col = col.lower()
    date = date.split('/')
    day, month, year = int(date[0]), int(date[1]), int(date[2])

    print(f"Command received from server: {ctx.guild.name}")

    btkID = btkID.upper()

    if btkID == 'BENTO':
        btkID = 'BENTOJANA'
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'VICKY 2020', 'JOYCE 2018', 'GORDON 1979', 'BENI 2003', 'MARK 1992', 'NADINE 1978',
                  'WINNIE 1978', 'HARVEY 2005', 'FREDA 1981', 'POLLY 1971', 'LOUISE 1970', 'LUCY 1962', 'CARMEN 1974']
    
    check = f"{btkID} {yr}"
    
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    if(btkID == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    if(btkID == 'UNNAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    
    def _00x_to_xx00(des):
        convert_map = {"L": "AL", "E": "EP", "C": "CP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[A-Z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    #Load in the loops for finding the latitude and longitude...

    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, DateTime = 0, 0, ""
    storm_name = ""
    s_ID = ""
    idl = False
    basin = ''
    hx = int(hour[:2])
    await ctx.send("Please wait. Due to my terrible potato laptop, the dataset may take a while to go through.")

    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]):
                    DateTime = lines[6]
                    basin = lines[3]
                    if int(DateTime[:4]) == year and int(DateTime[5:7]) == month and int(DateTime[8:10]) == day and int(DateTime[-8:-6]) == hx:
                        s_ID = lines[18]
                        cdy, cdx = float(lines[19]), float(lines[20])
                        if(float(cdx) <= -173.5 or float(cdx) >= 173.5):
                            idl = True
                        storm_name = lines[5]
                        break
    
    if cdx == 0:
        await ctx.send("Error 404: Storm not found. Please check if your entry is correct.")
        return

    await ctx.send("System located in database, fetching appropriate satellite...")

    center_lat = cdy # Center latitude
    center_lon = cdx # Center longitude
    extent = 8  # Extent in degrees
    #print(cdy, "", cdx)

    if col == 'random':
        import random
        import inspect
        functions = [func for name, func in inspect.getmembers(cmap_collection, inspect.isfunction)]
        cmap_func = random.choice(functions)
        await ctx.send(f"Selected function: {cmap_func.__name__}")
    else:
        cmap_func = getattr(cmap_collection, col)

    # Now call it
    cmap, vmax, vmin = cmap_func()

    def satellite_mapping(cdx, day, month, year):
        date = datetime(year, month, day)
        if cdx > -105 and cdx < 10: #Atlantic
            if datetime(1978, 2, 18) <= date <= datetime(1979, 1, 19):
                return "GOES2"
            if datetime(1979, 1, 21) <= date <= datetime(1979, 4, 19):
                return "SMS1"
            if datetime(1979, 4, 20) <= date <= datetime(1981, 8, 5):
                return "SMS2"
            if datetime(1981, 8, 6) <= date <= datetime(1984, 7, 29):
                return "GOES5"
            if datetime(1987, 3, 25) <= date <= datetime(1994, 8, 30):
                return "GOES7"
            if datetime(1994, 8, 31) <= date <= datetime(2003, 4, 1):
                return "GOES8"
            if datetime(2003, 4, 2) <= date <= datetime(2010, 4, 14):
                return "GOES12"
            if datetime(2010, 4, 15) <= date <= datetime(2017, 12, 31):
                return "GOES13"
            return "GOES16"
        if cdx <= 180 and cdx > 100: #WPAC + AUS
            if datetime(1978, 11, 30) <= date <= datetime(1979, 12, 1):
                return "GMS1"
            if datetime(1998, 11, 10) <= date <= datetime(2003, 4, 22):
                return "GMS5"
            if datetime(2003, 4, 23) <= date <= datetime(2005, 11, 17):
                return "GOES9"
            if (datetime(2005, 11, 18) <= date <= datetime(2010, 7, 10)) or (datetime(2010, 11, 1) <= date <= datetime(2010, 12, 21)) or (datetime(2012, 10, 18) <= date <= datetime(2012, 12, 26)) or (datetime(2013, 10, 22) <= date <= datetime(2013, 12, 18)):
                return "MTSAT1R"
            if (datetime(2010, 7, 11) <= date <= datetime(2010, 10, 31)) or (datetime(2010, 12, 22) <= date <= datetime(2012, 10, 17)) or (datetime(2012, 12, 27) <= date <= datetime(2013, 10, 21)) or (datetime(2013, 12, 19) <= date <= datetime(2015, 7, 6)):
                return "MTSAT2"
            if datetime(2015, 7, 6) <= date <= datetime(2022, 12, 24):
                return "HIMAWARI8"
            return "HIMAWARI9"
        if cdx >= -180 and cdx <= -105: #EPAC + SPAC 
            if datetime(1978, 2, 18) <= date <= datetime(1978, 11, 20):
                return "GOES2"
            if datetime(1978, 11, 21) <= date <= datetime(1981, 3, 4):
                return "GOES3"
            if datetime(1981, 3, 5) <= date <= datetime(1982, 11, 25):
                return "GOES4"
            if datetime(1982, 11, 29) <= date <= datetime(1983, 5, 31):
                return "GOES1"
            if datetime(1983, 6, 1) <= date <= datetime(1989, 1, 20):
                return "GOES6"
            if datetime(1989, 1, 21) <= date <= datetime(1996, 1, 1):
                return "GOES7"
            if datetime(1995, 8, 31) <= date <= datetime(1998, 7, 21):
                return "GOES9"
            if datetime(1998, 7, 22) <= date <= datetime(2006, 6, 21):
                return "GOES10"
            if datetime(2006, 6, 22) <= date <= datetime(2011, 12, 6):
                return "GOES11"
            if datetime(2011, 12, 6) <= date <= datetime(2019, 2, 28):
                return "GOES15"
            if datetime(2019, 3, 1) <= date <= datetime(2023, 2, 27):
                return "GOES17"
            return "GOES18"
        if cdx < 100 and cdx > 30: #Indian Ocean
            if datetime(1978, 12, 2) <= date <= datetime(1979, 12, 1):
                return "GOES1"
            if datetime(1999, 3, 5) <= date <= datetime(2007, 1, 25):
                return "MET5"
            if datetime(2007, 1, 26) <= date <= datetime(2016, 10, 31):
                return "MET7"
            if datetime(2016, 11, 1) <= date <= datetime(2020, 12, 15):
                return "MET8"
            if datetime(2020, 12, 16) <= date <= datetime(2023, 4, 1):
                return "EWS-G1"
            if datetime(2023, 4, 2) <= date <= datetime(2023, 10, 25):
                return "MET9"
            return "EWS-G2"
        return "unknown"

    bandIRMapping = {'GOES1':8, 'GOES2':8, 'GOES3':8, 'GOES4':8,'GOES5': 8, 'GOES6':8, 
                     'GOES7': 8,'GOES8': 4, 'GOES9':4, 'GOES10':4,'EWS-G1':4, 'EWS-G2':4,
                     'GOES11':4, 'GOES12':4, 'GOES13':4, 'GOES15':4, 'GOES16':13,
                     'GOES17':13, 'GOES18':13, 'GMS1':8, 'GMS5':2, 'MTSAT1R':2,
                     'MTSAT2':2, 'HIMAWARI8':13, 'HIMAWARI9':13, 'MET5':8, 
                     'MET7':8, 'MET8':9, 'MET9':9, 'SMS1':8, 'SMS2':8}

    satellite = satellite_mapping(cdx, day, month, year)
    if satellite == 'unknown':
        await ctx.send("Could not locate satellite, not in SSEC Inventory. Use Gridsat instead.")
        return
    import random
    api_key = ['API_KEY', 'API_KEY2', 'API_KEY3']
    center_lon *= -1
    size = 350
    extent_margin = 6.5

    if satellite in ['GOES5', 'GOES7']:
        if hour == '0000':
            from datetime import timedelta
            currdate = datetime(year, month, day)
            prevdate = currdate - timedelta(days=1)
            year, month, day = prevdate.year, prevdate.month, prevdate.day
            hour ='2331'
        else:
            hour = str(int(hour[:2])-1).zfill(2) + '31'

    url = f'https://mcfetch.ssec.wisc.edu/cgi-bin/mcfetch?dkey={random.choice(api_key)}&satellite={satellite}&band={bandIRMapping[satellite]}&output=NETCDF&date={year}-{str(month).zfill(2)}-{str(day).zfill(2)}&time={hour[:2]}:{hour[2:]}&lat={center_lat}+{center_lon}&mag=1+1&unit=TEMP'

    if satellite in ['GOES16', 'GOES17', 'GOES18', 'GOES19', 'HIMAWARI8', 'HIMAWARI9', 'MET8']:
        size = 500
        extent_margin = 5
        url += '&coverage=FD'
    if satellite == 'MTSAT1R' and hour[:2] in ['00', '06', '12', '18'] and cdy > 0:
        url += '&coverage=NH'
    url += f'&size={size}+{size}'

    print("Downloading the requested file...")
    print(url)
    
    import urllib3
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    
    if response.status == 200:
        try: 
            nc_data = xr.open_dataset(BytesIO(response.data))
        except ValueError:
            await ctx.send("The mcfetch file either does not exist or inputs were incorrect. Try again or use gridsat instead.")
            return
        print("Successful response, plotting...")
        data = nc_data['data'].squeeze()
        if satellite in ['GOES7']:
            data /= 10
        lat = nc_data['lat']
        lon = nc_data['lon']

        projection = ccrs.PlateCarree() if idl==False else ccrs.PlateCarree(central_longitude=180)
        plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=projection)
        #data = np.squeeze(data)  # Ensure shape is (SIZE, SIZE)

        # Slice the region within ±1° around the center
        subset = data.where((lat >= cdy - 1) & (lat <= cdy + 1) &
                            (lon >= cdx - 1) & (lon <= cdx + 1))

        valid_pixels = subset
        max_bt_kelvin = valid_pixels.max().item()
        max_bt_celsius = max_bt_kelvin - 273.15

        if idl:
            lon = xr.where(lon < 0, lon + 180, lon - 180)

        import datetime

        # Access the 'time' variable and get its value
        time_value = nc_data['time'].values

        # Convert the time value (seconds since epoch) to a datetime object
        # The time variable has a 'units' attribute indicating it's seconds since 1970-1-1 0:0:0
        # We need to convert the seconds since epoch to a timedelta and add it to the epoch start
        epoch_start = np.datetime64('1970-01-01T00:00:00Z')
        time_difference = time_value[0] - epoch_start
        seconds_since_epoch = time_difference.astype('timedelta64[s]').item().total_seconds()

        # Convert the seconds since epoch to a datetime object
        datetime_obj = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=seconds_since_epoch)
        time_string = datetime_obj.strftime('%H:%M')
        date_string = datetime_obj.strftime('%d/%m/%Y')
        if idl:
            adjusted_cdx = (cdx + 180) % 360  # Wrap to 0–360 if necessary
        else:
            adjusted_cdx = cdx
        ax.set_extent([adjusted_cdx - extent_margin, adjusted_cdx + extent_margin, cdy - extent_margin, cdy + extent_margin], crs=projection)

        #----DEBUG-----
        
        # Convert to NumPy arrays
        lat_np = np.asarray(lat.values, dtype=float)
        lon_np = np.asarray(lon.values, dtype=float)
        data_np = np.asarray(data.values.squeeze(), dtype=float)

        # Fill invalid coords
        bad = ~(np.isfinite(lat_np) & np.isfinite(lon_np))
        if bad.any():
            # Hide data in those cells
            data_np[bad] = np.nan
            # Fill lat/lon so pcolormesh doesn't crash
            # Option 1: nearest neighbor fill (safe for Cartopy)
            lat_np[bad] = np.interp(np.flatnonzero(bad), np.flatnonzero(~bad), lat_np[~bad])
            lon_np[bad] = np.interp(np.flatnonzero(bad), np.flatnonzero(~bad), lon_np[~bad])

        pcolor = ax.pcolormesh(lon_np, lat_np, data_np, cmap=cmap, vmax=vmax, vmin=vmin, transform=projection)

        ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
        ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
        
        ax.set_title(f'MCFETCH Band {str(bandIRMapping[satellite]).zfill(2)} Brightness Temperature IR | {time_string} UTC {date_string}\n{s_ID} {storm_name} | Satellite: {satellite} | Max center temp: {max_bt_celsius:.2f}°C')

        ax.set_xlabel('Longitude (degrees)')
        ax.set_ylabel('Latitude (degrees)')
        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels = False
        gls.right_labels = False
        gls.xlocator = mticker.FixedLocator(range(-180, 181, 2))  # Control gridline spacing
        gls.ylocator = mticker.FixedLocator(range(-90, 91, 2))
        #gl.xformatter = LONGITUDE_FORMATTER
        gls.yformatter = LATITUDE_FORMATTER
        gls.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
        gls.ylabel_style = {'size': 8, 'color': 'w'}
        
        import matplotlib.ticker as ticker
        cbar = plt.colorbar(pcolor, ax=ax, orientation='vertical', shrink=1, pad=0.02)
        from matplotlib.ticker import MultipleLocator, FuncFormatter

        celsius_ticks = np.arange(vmin-273.15, vmax+1-273.15, 10)  # Adjust as needed
        kelvin_ticks = celsius_ticks + 273.15

        cbar.set_ticks(kelvin_ticks)
        cbar.set_ticklabels([f"{c:.0f}" for c in celsius_ticks])
        cbar.set_label(f"Brightness Temperature (°C) | Colorscale: {cmap_func.__name__}")

        plt.tight_layout()
        image_path = f'mcfetch_nc{random.randint(1, 100)}.png'
        plt.savefig(image_path, format='png', bbox_inches='tight')
        plt.close()

        async def send_image(image_path):
            with open(image_path, 'rb') as image_file:
                image = discord.File(image_file)
                await ctx.send(file=image)

        # Send the generated image
        await send_image(image_path)

        # Remove the temporary image file
        os.remove(image_path)
        #os.remove("temp.nc")
    else:
        await ctx.data(f"Request unfortunately failed.")
        return

@bot.command(name='mcfetch_pro')
async def mcfetch_pro(ctx, satellite, band, cdy:float, cdx:float, hour, date, col:str, coverage=''):
    import matplotlib.style as mplstyle
    import cmap_collection
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import os
    from io import BytesIO
    from matplotlib.colors import ListedColormap, LinearSegmentedColormap
    import matplotlib.ticker as mticker
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    from datetime import datetime
    mplstyle.use("dark_background") 
    
    idl = False
    if(float(cdx) <= -173.5 or float(cdx) >= 173.5):
        idl = True
    await ctx.send("System located in database, fetching appropriate satellite...")

    col = col.lower()
    date = date.split('/')
    day, month, year = int(date[0]), int(date[1]), int(date[2])

    print(f"Command received from server: {ctx.guild.name}")

    center_lat = cdy # Center latitude
    center_lon = cdx # Center longitude
    extent = 8  # Extent in degrees
    #print(cdy, "", cdx)

    if col == 'random':
        import random
        import inspect
        functions = [func for name, func in inspect.getmembers(cmap_collection, inspect.isfunction)]
        cmap_func = random.choice(functions)
        await ctx.send(f"Selected function: {cmap_func.__name__}")
    else:
        cmap_func = getattr(cmap_collection, col)

    # Now call it
    cmap, vmax, vmin = cmap_func()
    satellite = satellite.upper()

    import random
    api_key = ['API_KEY', 'API_KEY2', 'API_KEY3']
    center_lon *= -1
    size = 350
    extent_margin = 6.5

    url = f'https://mcfetch.ssec.wisc.edu/cgi-bin/mcfetch?dkey={random.choice(api_key)}&satellite={satellite}&band={band}&output=NETCDF&date={year}-{str(month).zfill(2)}-{str(day).zfill(2)}&time={hour[:2]}:{hour[2:]}&lat={center_lat}+{center_lon}&mag=1+1&unit=TEMP'
    

    if coverage != '':
        url +=  f'&coverage={coverage}'
        extent_margin = 5
        size = 500
    url += f'&size={size}+{size}'

    print("Downloading the requested file...")
    print(url)
    
    import urllib3
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    
    if response.status == 200:
        try: 
            nc_data = xr.open_dataset(BytesIO(response.data))
        except ValueError:
            await ctx.send("The mcfetch file either does not exist or inputs were incorrect. Try again or use gridsat instead.")
            return
        print("Successful response, plotting...")
        data = nc_data['data'].squeeze()
        if satellite in ['GOES7']:
            data /= 10
        lat = nc_data['lat']
        lon = nc_data['lon']

        import datetime
        # Access the 'time' variable and get its value
        time_value = nc_data['time'].values

        # Convert the time value (seconds since epoch) to a datetime object
        # The time variable has a 'units' attribute indicating it's seconds since 1970-1-1 0:0:0
        # We need to convert the seconds since epoch to a timedelta and add it to the epoch start
        epoch_start = np.datetime64('1970-01-01T00:00:00Z')
        time_difference = time_value[0] - epoch_start
        seconds_since_epoch = time_difference.astype('timedelta64[s]').item().total_seconds()

        # Convert the seconds since epoch to a datetime object
        datetime_obj = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=seconds_since_epoch)
        time_string = datetime_obj.strftime('%H:%M')
        date_string = datetime_obj.strftime('%d/%m/%Y')
        projection = ccrs.PlateCarree() if idl==False else ccrs.PlateCarree(central_longitude=180)
        plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=projection)
        #data = np.squeeze(data)  # Ensure shape is (SIZE, SIZE)

        # Slice the region within ±1° around the center
        subset = data.where((lat >= cdy - 1) & (lat <= cdy + 1) &
                            (lon >= cdx - 1) & (lon <= cdx + 1))

        # Mask invalid values and find max
        valid_pixels = subset
        max_bt_kelvin = valid_pixels.max().item()
        max_bt_celsius = max_bt_kelvin - 273.15

        if idl:
            lon = xr.where(lon < 0, lon + 180, lon - 180)

        if idl:
            adjusted_cdx = (cdx + 180) % 360  # Wrap to 0–360 if necessary
        else:
            adjusted_cdx = cdx
        ax.set_extent([adjusted_cdx - extent_margin, adjusted_cdx + extent_margin, cdy - extent_margin, cdy + extent_margin], crs=projection)

        #----DEBUG-----
        
        # Convert to NumPy arrays
        lat_np = np.asarray(lat.values, dtype=float)
        lon_np = np.asarray(lon.values, dtype=float)
        data_np = np.asarray(data.values.squeeze(), dtype=float)

        # Fill invalid coords
        bad = ~(np.isfinite(lat_np) & np.isfinite(lon_np))
        if bad.any():
            # Hide data in those cells
            data_np[bad] = np.nan
            # Fill lat/lon so pcolormesh doesn't crash
            # Option 1: nearest neighbor fill (safe for Cartopy)
            lat_np[bad] = np.interp(np.flatnonzero(bad), np.flatnonzero(~bad), lat_np[~bad])
            lon_np[bad] = np.interp(np.flatnonzero(bad), np.flatnonzero(~bad), lon_np[~bad])

        pcolor = ax.pcolormesh(lon_np, lat_np, data_np, cmap=cmap, vmax=vmax, vmin=vmin, transform=projection)

        ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
        ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
        
        ax.set_title(f'MCFETCH Band {str(band).zfill(2)} Brightness Temperature | {time_string} UTC {date_string}\n({cdy}, {cdx}) | Satellite: {satellite} | Max center temp: {max_bt_celsius:.2f}°C')

        ax.set_xlabel('Longitude (degrees)')
        ax.set_ylabel('Latitude (degrees)')
        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels = False
        gls.right_labels = False
        gls.xlocator = mticker.FixedLocator(range(-180, 181, 2))  # Control gridline spacing
        gls.ylocator = mticker.FixedLocator(range(-90, 91, 2))
        #gl.xformatter = LONGITUDE_FORMATTER
        gls.yformatter = LATITUDE_FORMATTER
        gls.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
        gls.ylabel_style = {'size': 8, 'color': 'w'}
        
        import matplotlib.ticker as ticker
        cbar = plt.colorbar(pcolor, ax=ax, orientation='vertical', shrink=1, pad=0.02)
        from matplotlib.ticker import MultipleLocator, FuncFormatter

        celsius_ticks = np.arange(vmin-273.15, vmax+1-273.15, 10)  # Adjust as needed
        kelvin_ticks = celsius_ticks + 273.15

        cbar.set_ticks(kelvin_ticks)
        cbar.set_ticklabels([f"{c:.0f}" for c in celsius_ticks])
        cbar.set_label(f"Brightness Temperature (°C) | Colorscale: {cmap_func.__name__}")

        plt.tight_layout()
        image_path = f'mcfetch_nc{random.randint(1, 100)}.png'
        plt.savefig(image_path, format='png', bbox_inches='tight')
        plt.close()

        async def send_image(image_path):
            with open(image_path, 'rb') as image_file:
                image = discord.File(image_file)
                await ctx.send(file=image)

        # Send the generated image
        await send_image(image_path)

        # Remove the temporary image file
        os.remove(image_path)
        #os.remove("temp.nc")
    else:
        await ctx.data(f"Request unfortunately failed.")
        return

@bot.command(name='cmap_help')
async def cmap_help(ctx):
    import cmap_counter

    await ctx.send(f"List of IR colorscales: {cmap_counter.ir}\n\nList of WV colorscales: {cmap_counter.wv}")
    
@bot.command(name='mcfetch_help')
async def mcfetch_help(ctx):
    image2 = 'MCFETCH_SATELLITESv2.webp'
    image1 = 'documentation.webp'
    with open(image1, 'rb') as image_file:
        image1 = discord.File(image_file)
        await ctx.send(file=image1)
    await ctx.send("Bands available on each satellite under the !mcfetch command:")
    with open(image2, 'rb') as image_file:
        image2 = discord.File(image_file)
        await ctx.send(file=image2)

@bot.command(name = 'ncep')
async def ncep(ctx, hour:str, day:str, month:str, year:str, area_north='90', area_south='-90', area_west='-180', area_east='180', colormap='temp_19lev'):
    import requests
    from io import BytesIO
    await ctx.send("Please wait as the data is plotted and generated.")
    if int(year) <= 2015:
        url = f'https://psl.noaa.gov/cgi-bin/mddb2/plot.pl?doplot=1&varID=141364&fileID=0&itype=0&variable=pres&levelType=Surface&level_units=&level=Surface&timetype=8x&fileTimetype=8x&year1={year}&month1={month}&day1={day}&hr1={hour.zfill(2)}%20Z&year2=2015&month2=12&day2=31&hr2=00%20Z&vectorPlot=0&contourLevel=custom&cint=100&lowr=98000&highr=102000&colormap={colormap}&reverseColormap=no&contourlines=1&colorlines=1&contourfill=1&contourlabels=1&removezonal=0&boundary=Geophysical&projection=CylindricalEquidistant&region=Custom&area_north={area_north}&area_west={area_west}&area_east={area_east}&area_south={area_south}&centerLat=0.0&centerLon=270.0&mapfill=0'
    else:
        url = f'https://psl.noaa.gov/cgi-bin/mddb2/plot.pl?doplot=1&varID=158846&fileID=0&itype=0&variable=slp&levelType=Sea%20Level&level_units=&level=Sea%20Level&timetype=4x&fileTimetype=4x&year1={year}&month1={month}&day1={day}&hr1={hour.zfill(2)}%20Z&year2=2024&month2=5&day2=30&hr2=00%20Z&vectorPlot=0&contourLevel=custom&cint=100&lowr=98000&highr=102000&colormap={colormap}&reverseColormap=no&contourlines=1&colorlines=1&contourfill=1&contourlabels=1&removezonal=0&boundary=Geophysical&projection=CylindricalEquidistant&region=Custom&area_north={area_north}&area_west={area_west}&area_east={area_east}&area_south={area_south}&centerLat=0.0&centerLon=270.0&mapfill=0'
    response = requests.get(url)
    if response.status_code == 200:
        response = requests.get(url)
        image_data = BytesIO(response.content)
        await ctx.send(file=discord.File(image_data, 'ncep.jpg'))
    else:
        await ctx.send("Error 404: The image either does not exist or is yet to be created.")

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

@bot.command(name='weatherunion')
async def weatherunion(ctx, stn_id:str):
    stn_id = stn_id.upper()
    import requests

    if stn_id == "HELP":
        await ctx.send("A list of all station IDs supported by this command:")
        await ctx.send("https://b.zmtcdn.com/data/file_assets/65fa362da3aa560a92f0b8aeec0dfda31713163042.pdf")
        return

    # Define the API endpoint URL
    url = 'https://weatherunion.com/gw/weather/external/v0/get_locality_weather_data'

    # Define the headers with the required content-type and your API key
    headers = {
        'content-type': 'application/json',
        'x-zomato-api-key': '0b96804b60bf26c471255275a86f4d6e'
    }

    # Define the parameters (locality_id)
    params = {
        'locality_id': stn_id
    }

    # Make a GET request to the API
    response = requests.get(url, headers=headers, params=params)
    result = ""
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Extract relevant information from the response
        status = data['status']
        message = data['message']
        device_type = data['device_type']
        locality_weather_data = data['locality_weather_data']
        
        # Print the extracted information
        result += (f"```Status: {status}")
        result += (f"\nMessage: {message}")
        result += (f"\nDevice Type: {device_type}")
        result += ("\nLocality Weather Data:")
        result += (f"\nTemperature: {locality_weather_data['temperature']} °C")
        result += (f"\nHumidity: {locality_weather_data['humidity']} %")
        result += (f"\nWind Speed: {locality_weather_data['wind_speed']} m/s, {(float(locality_weather_data['wind_speed'])*1.944):.2f} kts")
        result += (f"\nWind Direction: {locality_weather_data['wind_direction']} degrees")
        result += (f"\nRain Intensity: {locality_weather_data['rain_intensity']} mm/min")
        result += (f"\nRain Accumulation: {locality_weather_data['rain_accumulation']} mm```")
        await ctx.send(result)
    else:
        await ctx.send(f"Error: {response.status_code} - {response.reason}")

@bot.command(name='gridsat_custom')
async def gridsat_custom(ctx, lat:float, lon:float, hour:int, time:str, col:str, override = ''):
    import matplotlib.style as mplstyle
    import cmap_collection
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import requests
    import os
    from matplotlib.colors import ListedColormap, LinearSegmentedColormap
    import matplotlib.ticker as mticker
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    mplstyle.use("dark_background") 
    await ctx.send('Request received, downloading data...')
    col = col.lower()
    time = time.split('/')
    day, month, year = (time[0]).zfill(2), (time[1]).zfill(2), time[2]

    center_lat = lat # Center latitude
    center_lon = lon # Center longitude
    extent = 8  # Extent in degrees
    #print(cdy, "", cdx)
    if col == 'random':
        import random
        import inspect
        functions = [func for name, func in inspect.getmembers(cmap_collection, inspect.isfunction)]
        cmap_func = random.choice(functions)
        await ctx.send(f"Selected function: {cmap_func.__name__}")
    else:
        cmap_func = getattr(cmap_collection, col)

    # Now call it
    cmap, vmax, vmin = cmap_func()

    destination = 'gridsatfile.nc'

    # Calculate the bounds
    lat_min, lat_max = center_lat - extent, center_lat + extent
    def normalize_lon(lon):
        return ((lon + 180) % 360) - 180

    lon_min = normalize_lon(center_lon - extent)
    lon_max = normalize_lon(center_lon + extent)

    idl = lon_min > lon_max

    from datetime import datetime

    def get_satellite(year, month, day, cdx):
        date = datetime(year, month, day)

        if (cdx > -105 and cdx < -5) or override == '1':
            if datetime(1994, 8, 31) <= date <= datetime(2003, 4, 1):
                return "goes08"
            elif datetime(2003, 4, 2) <= date <= datetime(2010, 4, 14):
                return "goes12"
            elif datetime(2010, 4, 15) <= date <= datetime(2017, 12, 31):
                return "goes13"
        elif cdx < 180 and cdx > 120:
            if datetime(2003, 4, 23) <= date <= datetime(2005, 11, 17):
                return "goes09"
        else:
            if datetime(1995, 8, 31) <= date <= datetime(1998, 7, 21):
                return "goes09"
            elif datetime(1998, 7, 22) <= date <= datetime(2006, 6, 21):
                return "goes10"
            elif datetime(2006, 6, 22) <= date <= datetime(2011, 12, 6):
                return "goes11"
            elif datetime(2011, 12, 6) <= date <= datetime(2017, 11, 29):
                return "goes15"

        return "unknown"

    satellite = ''
    if center_lon >= 150 or center_lon <= -5 and idl == False: 
        satellite = get_satellite(int(year), int(month), int(day), lon)
    else:
        satellite = 'unknown'

    def download_subset_nc(year, month, day, hour, lat_min, lat_max, lon_min, lon_max):
        file1 = f"gridsatfile_part1.nc"
        file2 = f"gridsatfile_part2.nc"
        destination = "gridsatfile.nc"
        if satellite == 'unknown':
            base_url = "https://www.ncei.noaa.gov/thredds/ncss/cdr/gridsat"
            filename = f"GRIDSAT-B1.{year}.{str(month).zfill(2)}.{str(day).zfill(2)}.{str(hour).zfill(2)}.v02r01.nc"
            
            # Detect IDL crossing
            if idl == False:
                # Normal case
                subset_url = f"{base_url}/{year}/{filename}?var=irwin_cdr&north={lat_max}&south={lat_min}&east={lon_max}&west={lon_min}&accept=netcdf"
                response = requests.get(subset_url)
                if response.status_code == 200:
                    with open(destination, "wb") as f:
                        f.write(response.content)
                    print("Subset downloaded successfully.")
                else:
                    print(f"Failed to download subset. Status code: {response.status_code}")
            else:
                # Wraparound case
                url1 = f"{base_url}/{year}/{filename}?var=irwin_cdr&north={lat_max}&south={lat_min}&east=180&west={lon_min}&accept=netcdf"
                url2 = f"{base_url}/{year}/{filename}?var=irwin_cdr&north={lat_max}&south={lat_min}&east={lon_max}&west=-180&accept=netcdf"
                
                success = True

                for url, fname in zip([url1, url2], [file1, file2]):
                    res = requests.get(url)
                    if res.status_code == 200:
                        with open(fname, "wb") as f:
                            f.write(res.content)
                        print(f"{fname} downloaded successfully.")
                    else:
                        print(f"Failed to download {fname}. Status code: {res.status_code}")
                        success = False
                
                if success:
                    # Merge files
                    ds1 = xr.open_dataset(file1, decode_times=False)
                    ds2 = xr.open_dataset(file2, decode_times=False)
                    merged = xr.concat([ds1, ds2], dim="lon")
                    merged.to_netcdf(destination)
                    ds1.close()
                    ds2.close()
                    os.remove(file1)
                    os.remove(file2)
                    print("Merged files across IDL successfully.")
                else:
                    print("Data download failed for one or both segments.")
        else:
            base_url = "https://www.ncei.noaa.gov/thredds/ncss/satellite/gridsat-goes-full-disk"
            filename = f"GridSat-GOES.{satellite}.{year}.{str(month).zfill(2)}.{str(day).zfill(2)}.{str(hour).zfill(2)}00.v01.nc"
            
            if idl == False or idl == True:
                if idl == True:
                    if lon_min > 0:
                        lon_min = lon_min - 360
                    if lon_max > 0:
                        lon_max = lon_max - 360
                subset_url = f"{base_url}/{year}/{str(month).zfill(2)}/{filename}?var=ch4&maxy={lat_max}&miny={lat_min}&maxx={lon_max}&minx={lon_min}&accept=netcdf"  
                response = requests.get(subset_url)
                if response.status_code == 200:
                    with open("gridsatfile.nc", "wb") as f:
                        f.write(response.content)
                    print("Subset downloaded successfully.")
                else:
                    print(f"Failed to download subset. Status code: {response.status_code}")
            else:
                url1 = f"{base_url}/{year}/{str(month).zfill(2)}/{filename}?var=ch4&maxy={lat_max}&miny={lat_min}&maxx={((lon_min + 180) % 360) - 180}&minx=-180&accept=netcdf"
                url2 = f"{base_url}/{year}/{str(month).zfill(2)}/{filename}?var=ch4&maxy={lat_max}&miny={lat_min}&maxx={lon_max}&minx=-180&accept=netcdf"
                
                success = True

                for url, fname in zip([url1, url2], [file1, file2]):
                    res = requests.get(url)
                    if res.status_code == 200:
                        with open(fname, "wb") as f:
                            f.write(res.content)
                        print(f"{fname} downloaded successfully.")
                    else:
                        print(f"Failed to download {fname}. Status code: {res.status_code}")
                        success = False
                
                if success:
                    # Merge files
                    ds1 = xr.open_dataset(file1, decode_times=False)
                    ds2 = xr.open_dataset(file2, decode_times=False)
                    merged = xr.concat([ds1, ds2], dim="lon")
                    merged.to_netcdf(destination)
                    ds1.close()
                    ds2.close()
                    os.remove(file1)
                    os.remove(file2)
                    print("Merged files across IDL successfully.")
                else:
                    print("Data download failed for one or both segments.")

    download_subset_nc(year, month, day, hour, lat_min, lat_max, lon_min, lon_max)

    await ctx.send('Data download successful, plotting values...')

    # Load the NetCDF file
    dataset = xr.open_dataset(destination, decode_times=False)

    lat = dataset['lat']
    lon = dataset['lon']
    brightness_temp = dataset['irwin_cdr'] if satellite == 'unknown' else dataset['ch4']
    #print("Longitude min/max:", lon[0].values, lon[-1].values)

    brightness_temp_slice = brightness_temp.isel(time=0)
    if idl == True and satellite == 'unknown':
        def remap_longitudes(lon_array):
            return ((lon_array + 180) % 360) - 180

        # Apply it directly to the coordinate
        brightness_temp_slice = brightness_temp_slice.assign_coords(lon=remap_longitudes(brightness_temp_slice.lon)).sortby('lon')

    def get_brightness_temp_subset(brightness_temp_slice, lat_min, lat_max, lon_min, lon_max):
        if idl == False or satellite != 'unknown':
            subset = brightness_temp_slice.sel(
                lat=slice(lat_min, lat_max),
                lon=slice(lon_min, lon_max)
            )
        else:
            if satellite == 'unknown':
                # IDL wraparound
                part1 = brightness_temp_slice.sel(
                    lat=slice(lat_min, lat_max),
                    lon=slice(lon_min, 180)
                )
                part2 = brightness_temp_slice.sel(
                    lat=slice(lat_min, lat_max),
                    lon=slice(-180, lon_max)
                )
                subset = xr.concat([part1, part2], dim="lon")
        
        return subset

    # Select data within the specified bounds
    selected_lat = lat[(lat >= lat_min) & (lat <= lat_max)]
    if idl == False or satellite != 'unknown':
        selected_lon = lon[(lon >= lon_min) & (lon <= lon_max)]
        selected_brightness_temp = brightness_temp_slice.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    else:
         # IDL case: wrap-around
        if satellite == 'unknown':
            selected_lon = lon[(lon >= lon_min) | (lon <= lon_max)]
            selected_brightness_temp = get_brightness_temp_subset(brightness_temp_slice, lat_min, lat_max, lon_min, lon_max)
    
    # Select eye temperature data within the specified bounds
    selected_eye_temp = brightness_temp_slice.sel(lat=slice(center_lat-1, center_lat+1), lon=slice(center_lon-1, center_lon+1))

    def kelvin_to_celsius(kelvin_temp):
        celsius_temp = np.array(kelvin_temp) - 273.15
        return celsius_temp

    selected_brightness_temp = kelvin_to_celsius(selected_brightness_temp.values)
    try:
        eye_temp = brightness_temp_slice.sel(
            lat=center_lat,
            lon=center_lon,
            method="nearest"
        )
        max_temp = "{:.2f}".format(np.max(selected_eye_temp.values))
    except KeyError:
        await ctx.send("Could not locate eye temperature: storm center may be off the data grid.")
        max_temp = "N/A"

    def kelvin_to_celsius(kelvin_temp):
        celsius_temp = float(kelvin_temp) - 273.15
        return "{:.2f}".format(celsius_temp)

    if selected_brightness_temp.size == 0:
        await ctx.send("Plotting error: No data found in selected region.")
        return

    projection = ccrs.PlateCarree() if idl == False else ccrs.PlateCarree(central_longitude=180)

    plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=projection)
    if idl:
        selected_lon_plot = xr.where(selected_lon < 0, selected_lon + 180, selected_lon - 180)
    else:
        selected_lon_plot = selected_lon
    
    pcolor = ax.pcolormesh(selected_lon_plot, selected_lat, selected_brightness_temp, cmap=cmap, transform=projection, vmax=vmax-273.15, vmin=vmin-273.15)
    #ax.set_extent([lon[-1], lon[0], lat[-1], lat[0]], crs=ccrs.PlateCarree())
    from matplotlib import colors      
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    #ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    ax.set_xlabel('Longitude (degrees)')
    ax.set_ylabel('Latitude (degrees)')
    
    if satellite != 'unknown':
        ax.set_title(f'GRIDSAT-GOES Channel 4 Brightness Temperature IR | {str(hour).zfill(2)}:00 UTC {str(day).zfill(2)}/{str(month).zfill(2)}/{year}\n({center_lat}, {center_lon}) | {satellite[:-2].upper()}-{satellite[-2:]} | Max center temp = {kelvin_to_celsius(max_temp)} °C')
    else:
        ax.set_title(f'GRIDSAT B1 Brightness Temperature IR | {str(hour).zfill(2)}:00 UTC {str(day).zfill(2)}/{str(month).zfill(2)}/{year}\n({center_lat}, {center_lon}) | Max center temp = {kelvin_to_celsius(max_temp)} °C')
    gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gls.top_labels = False
    gls.right_labels = False
    gls.xlocator = mticker.FixedLocator(range(-180, 181, 2))  # Control gridline spacing
    gls.ylocator = mticker.FixedLocator(range(-90, 91, 2))
    #gl.xformatter = LONGITUDE_FORMATTER
    gls.yformatter = LATITUDE_FORMATTER
    gls.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
    gls.ylabel_style = {'size': 8, 'color': 'w'}
    

    import matplotlib.ticker as ticker
    cbar = plt.colorbar(pcolor, label=f'Brightness Temperature (Celcius) | Colorscale: {cmap_func.__name__}')
    cbar.locator = ticker.MultipleLocator(10)
    cbar.update_ticks()

    plt.tight_layout()
    image_path = f'_SST_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)

    dataset.close()
    os.remove(destination)

@bot.command(name='gridsat')
async def gridsat(ctx, btkID:str, yr:str, hour:int, time:str, col:str, override = ''):
    import matplotlib.style as mplstyle
    import csv
    import cmap_collection
    import xarray as xr
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import requests
    import os
    import matplotlib.ticker as mticker
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    mplstyle.use("dark_background") 

    col = col.lower()
    time = time.split('/')
    day, month, year = int(time[0]), int(time[1]), int(time[2])

    print(f"Command received from server: {ctx.guild.name}")

    btkID = btkID.upper()

    if btkID == 'BENTO':
        btkID = 'BENTOJANA'
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'VICKY 2020', 'JOYCE 2018', 'GORDON 1979', 'BENI 2003', 'MARK 1992', 'NADINE 1978',
                  'WINNIE 1978', 'HARVEY 2005', 'FREDA 1981', 'POLLY 1971', 'LOUISE 1970', 'LUCY 1962', 'CARMEN 1974']
    
    check = f"{btkID} {yr}"
    
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    if(btkID == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    if(btkID == 'UNNAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    
    def _00x_to_xx00(des):
        convert_map = {"L": "AL", "E": "EP", "C": "CP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[A-Z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    #Load in the loops for finding the latitude and longitude...

    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, DateTime = 0, 0, ""
    storm_name = ""
    s_ID = ""
    idl = False
    basin = ''
    await ctx.send("Please wait. Due to my terrible potato laptop, the dataset may take a while to go through.")
    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]):
                    DateTime = lines[6]
                    basin = lines[3]
                    if int(DateTime[:4]) == year and int(DateTime[5:7]) == month and int(DateTime[8:10]) == day and int(DateTime[-8:-6]) == hour:
                        s_ID = lines[18]
                        cdy, cdx = float(lines[19]), float(lines[20])
                        if(float(cdx) < -178 or float(cdx) > 178):
                            idl = True
                        storm_name = lines[5]
                        break
    
    if cdx == 0:
        await ctx.send("Error 404: Storm not found. Please check if your entry is correct.")
        return

    await ctx.send("System located in database, downloading data...")

    center_lat = cdy # Center latitude
    center_lon = cdx # Center longitude
    extent = 8  # Extent in degrees
    #print(cdy, "", cdx)
    if col == 'random':
        import random
        import inspect
        functions = [func for name, func in inspect.getmembers(cmap_collection, inspect.isfunction)]
        cmap_func = random.choice(functions)
        await ctx.send(f"Selected function: {cmap_func.__name__}")
    else:
        cmap_func = getattr(cmap_collection, col)

    # Now call it
    cmap, vmax, vmin = cmap_func()

    destination = 'gridsatfile.nc'

    # Calculate the bounds
    lat_min, lat_max = center_lat - extent, center_lat + extent
    def normalize_lon(lon):
        return ((lon + 180) % 360) - 180

    lon_min = normalize_lon(center_lon - extent)
    lon_max = normalize_lon(center_lon + extent)

    idl = lon_min > lon_max

    from datetime import datetime

    def get_satellite(basin, year, month, day, cdx):
        date = datetime(year, month, day)

        if cdx > -105 and cdx < -5 or override == '1':
            if datetime(1994, 8, 31) <= date <= datetime(2003, 4, 1):
                return "goes08"
            elif datetime(2003, 4, 2) <= date <= datetime(2010, 4, 14):
                return "goes12"
            elif datetime(2010, 4, 15) <= date <= datetime(2017, 12, 31):
                return "goes13"
        elif cdx < 180 and cdx > 120:
            if datetime(2003, 4, 23) <= date <= datetime(2005, 11, 17):
                return "goes09"
        else:
            if datetime(1995, 8, 31) <= date <= datetime(1998, 7, 21):
                return "goes09"
            elif datetime(1998, 7, 22) <= date <= datetime(2006, 6, 21):
                return "goes10"
            elif datetime(2006, 6, 22) <= date <= datetime(2011, 12, 6):
                return "goes11"
            elif datetime(2011, 12, 6) <= date <= datetime(2017, 11, 29):
                return "goes15"

        return "unknown"

    satellite = ''
    if cdx >= 150 or cdx <= -5: 
        satellite = get_satellite(basin, year, month, day, cdx)
    else:
        satellite = 'unknown'

    def download_subset_nc(year, month, day, hour, lat_min, lat_max, lon_min, lon_max):
        file1 = f"gridsatfile_part1.nc"
        file2 = f"gridsatfile_part2.nc"
        destination = "gridsatfile.nc"
        if satellite == 'unknown':
            base_url = "https://www.ncei.noaa.gov/thredds/ncss/grid/cdr/gridsat"
            filename = f"/GRIDSAT-B1.{year}.{str(month).zfill(2)}.{str(day).zfill(2)}.{str(hour).zfill(2)}.v02r01.nc"
            time = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}:00:00Z"
            # Detect IDL crossing
            if idl == False:
                # Normal case
                subset_url = f"{base_url}/{year}/{filename}?var=irwin_cdr&north={lat_max}&south={lat_min}&east={lon_max}&west={lon_min}&&time={time}&horizStride=1&vertStride=1&&accept=netcdf3"
                response = requests.get(subset_url)
                if response.status_code == 200:
                    with open(destination, "wb") as f:
                        f.write(response.content)
                    print("Subset downloaded successfully.")
                else:
                    print(f"Failed to download subset. Status code: {response.status_code}")
            else:
                # Wraparound case
                url1 = f"{base_url}/{year}/{filename}?var=irwin_cdr&north={lat_max}&south={lat_min}&east=180&west={lon_min}&&time={time}&horizStride=1&vertStride=1&&accept=netcdf3"
                url2 = f"{base_url}/{year}/{filename}?var=irwin_cdr&north={lat_max}&south={lat_min}&east={lon_max}&west=-180&&time={time}&horizStride=1&vertStride=1&&accept=netcdf3"
                
                success = True

                for url, fname in zip([url1, url2], [file1, file2]):
                    res = requests.get(url)
                    if res.status_code == 200:
                        with open(fname, "wb") as f:
                            f.write(res.content)
                        print(f"{fname} downloaded successfully.")
                    else:
                        print(f"Failed to download {fname}. Status code: {res.status_code}")
                        success = False
                
                if success:
                    # Merge files
                    ds1 = xr.open_dataset(file1, decode_times=False)
                    ds2 = xr.open_dataset(file2, decode_times=False)
                    merged = xr.concat([ds1, ds2], dim="lon")
                    merged.to_netcdf(destination)
                    ds1.close()
                    ds2.close()
                    os.remove(file1)
                    os.remove(file2)
                    print("Merged files across IDL successfully.")
                else:
                    print("Data download failed for one or both segments.")
        else:
            base_url = "https://www.ncei.noaa.gov/thredds/ncss/satellite/gridsat-goes-full-disk"
            filename = f"GridSat-GOES.{satellite}.{year}.{str(month).zfill(2)}.{str(day).zfill(2)}.{str(hour).zfill(2)}00.v01.nc"
            time = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}T{str(hour).zfill(2)}:00:00Z"
            if idl == True or idl == False:
                if idl:
                    if lon_max > 0:
                        lon_max -= 360
                    if lon_min > 0:
                        lon_min -= 360

                subset_url = f"{base_url}/{year}/{str(month).zfill(2)}/{filename}?var=ch4&maxy={lat_max}&miny={lat_min}&maxx={lon_max}&minx={lon_min}&&time={time}&&accept=netcdf3"  
                response = requests.get(subset_url)
                if response.status_code == 200:
                    with open("gridsatfile.nc", "wb") as f:
                        f.write(response.content)
                    print("Subset downloaded successfully.")
                else:
                    print(f"Failed to download subset. Status code: {response.status_code}")
            else:
                url1 = f"{base_url}/{year}/{str(month).zfill(2)}/{filename}?var=ch4&maxy={lat_max}&miny={lat_min}&maxx={((lon_min + 180) % 360) - 180}&minx=-180&&time={time}&&accept=netcdf3"
                url2 = f"{base_url}/{year}/{str(month).zfill(2)}/{filename}?var=ch4&maxy={lat_max}&miny={lat_min}&maxx={lon_max}&minx=-180&&time={time}&&accept=netcdf3"
                
                success = True

                for url, fname in zip([url1, url2], [file1, file2]):
                    res = requests.get(url)
                    if res.status_code == 200:
                        with open(fname, "wb") as f:
                            f.write(res.content)
                        print(f"{fname} downloaded successfully.")
                    else:
                        print(f"Failed to download {fname}. Status code: {res.status_code}")
                        success = False
                
                if success:
                    # Merge files
                    ds1 = xr.open_dataset(file1, decode_times=False)
                    ds2 = xr.open_dataset(file2, decode_times=False)
                    merged = xr.concat([ds1, ds2], dim="lon")
                    merged.to_netcdf(destination)
                    ds1.close()
                    ds2.close()
                    os.remove(file1)
                    os.remove(file2)
                    print("Merged files across IDL successfully.")
                else:
                    print("Data download failed for one or both segments.")

    download_subset_nc(year, month, day, hour, lat_min, lat_max, lon_min, lon_max)

    await ctx.send('Data download successful, plotting values...')

    # Load the NetCDF file
    dataset = xr.open_dataset(destination, decode_times=False)

    lat = dataset['lat']
    lon = dataset['lon']
    brightness_temp = dataset['irwin_cdr'] if satellite == 'unknown' else dataset['ch4']
    #print("Longitude min/max:", lon[0].values, lon[-1].values)


    #IDL case and Gridsat GOES:
    if idl and satellite != 'unknown':
        if 'time' in brightness_temp.dims:
            brightness_temp = brightness_temp.isel(time=0)
        lons_360 = lon % 360
        # If lon is a coordinate of ch4, make a copy with adjusted lons
        if 'lon' in brightness_temp.coords:
            brightness_temp = brightness_temp.assign_coords(lon=lons_360)

        # Sort by longitude to avoid wraparound issues
        brightness_temp = brightness_temp.sortby('lon')

        projection = ccrs.PlateCarree(central_longitude=180)
        plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=projection)

        brightness_temp['lon'] = xr.where(brightness_temp['lon'] < 0, brightness_temp['lon'] + 180, brightness_temp['lon'] - 180)

        pcolor = ax.pcolormesh(brightness_temp['lon'], brightness_temp['lat'], brightness_temp, cmap=cmap, transform=projection, vmax=vmax, vmin=vmin)
        ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
        ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
        #ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
        ax.set_xlabel('Longitude (degrees_east)')
        ax.set_ylabel('Latitude (degrees_north)')

        ax.set_title(f'GRIDSAT-GOES Channel 4 Brightness Temperature IR | {str(hour).zfill(2)}:00 UTC {str(day).zfill(2)}/{str(month).zfill(2)}/{year}\n{s_ID} {storm_name} | {satellite[:-2].upper()}-{satellite[-2:]} | Max center temp = N/A due to IDL')
        gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
        gls.top_labels = False
        gls.right_labels = False
        gls.xlocator = mticker.FixedLocator(range(-180, 181, 2))  # Control gridline spacing
        gls.ylocator = mticker.FixedLocator(range(-90, 91, 2))
        #gl.xformatter = LONGITUDE_FORMATTER
        gls.yformatter = LATITUDE_FORMATTER
        gls.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
        gls.ylabel_style = {'size': 8, 'color': 'w'}
        

        import matplotlib.ticker as ticker
        cbar = plt.colorbar(pcolor, label=f'Brightness Temperature (Celcius) | Colorscale: {cmap_func.__name__}')
        cbar.locator = ticker.MultipleLocator(10)
        cbar.update_ticks()

        plt.tight_layout()
        image_path = f'IDL_Map.png'
        plt.savefig(image_path, format='png', bbox_inches='tight')
        plt.close()

        async def send_image(image_path):
            with open(image_path, 'rb') as image_file:
                image = discord.File(image_file)
                await ctx.send(file=image)

        # Send the generated image
        await send_image(image_path)

        # Remove the temporary image file
        os.remove(image_path)

        dataset.close()
        os.remove(destination)
        return

    brightness_temp_slice = brightness_temp.isel(time=0)
    if idl == True and satellite == 'unknown':
        def remap_longitudes(lon_array):
            return ((lon_array + 180) % 360) - 180

        # Apply it directly to the coordinate
        brightness_temp_slice = brightness_temp_slice.assign_coords(lon=remap_longitudes(brightness_temp_slice.lon)).sortby('lon')

    def get_brightness_temp_subset(brightness_temp_slice, lat_min, lat_max, lon_min, lon_max):
        if idl == False:
            subset = brightness_temp_slice.sel(
                lat=slice(lat_min, lat_max),
                lon=slice(lon_min, lon_max)
            )
        else:
            # IDL wraparound
            part1 = brightness_temp_slice.sel(
                lat=slice(lat_min, lat_max),
                lon=slice(lon_min, 180)
            )
            part2 = brightness_temp_slice.sel(
                lat=slice(lat_min, lat_max),
                lon=slice(-180, lon_max)
            )
            subset = xr.concat([part1, part2], dim="lon")
        
        return subset

    # Select data within the specified bounds
    selected_lat = lat[(lat >= lat_min) & (lat <= lat_max)]
    if idl == False:
        selected_lon = lon[(lon >= lon_min) & (lon <= lon_max)]
        selected_brightness_temp = brightness_temp_slice.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
    else:
         # IDL case: wrap-around

        selected_lon = lon[(lon >= lon_min) | (lon <= lon_max)]
        selected_brightness_temp = get_brightness_temp_subset(brightness_temp_slice, lat_min, lat_max, lon_min, lon_max)
    
    # Select eye temperature data within the specified bounds
    selected_eye_temp = brightness_temp_slice.sel(lat=slice(center_lat-1, center_lat+1), lon=slice(center_lon-1, center_lon+1))

    def kelvin_to_celsius(kelvin_temp):
        celsius_temp = np.array(kelvin_temp) - 273.15
        return celsius_temp

    selected_brightness_temp = kelvin_to_celsius(selected_brightness_temp.values)
    try:
        eye_temp = brightness_temp_slice.sel(
            lat=center_lat,
            lon=center_lon,
            method="nearest"
        )
        max_temp = "{:.2f}".format(np.max(selected_eye_temp.values))
    except KeyError:
        await ctx.send("Could not locate eye temperature: storm center may be off the data grid.")
        max_temp = "N/A"

    def kelvin_to_celsius(kelvin_temp):
        celsius_temp = float(kelvin_temp) - 273.15
        return "{:.2f}".format(celsius_temp)

    if selected_brightness_temp.size == 0:
        await ctx.send("Plotting error: No data found in selected region.")
        return

    projection = ccrs.PlateCarree() if idl == False else ccrs.PlateCarree(central_longitude=180)

    plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=projection)
    if idl:
        selected_lon_plot = xr.where(selected_lon < 0, selected_lon + 180, selected_lon - 180)
    else:
        selected_lon_plot = selected_lon
    
    pcolor = ax.pcolormesh(selected_lon_plot, selected_lat, selected_brightness_temp, cmap=cmap, transform=projection, vmax=vmax-273.15, vmin=vmin-273.15)
    #ax.set_extent([lon[-1], lon[0], lat[-1], lat[0]], crs=ccrs.PlateCarree())
    from matplotlib import colors      
    ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor="c")
    ax.add_feature(cfeature.BORDERS, edgecolor="w", linewidth=0.75)
    #ax.add_feature(cfeature.LAND, facecolor=colors.to_rgba("c", 0.25))
    ax.set_xlabel('Longitude (degrees_east)')
    ax.set_ylabel('Latitude (degrees_north)')
    
    if satellite != 'unknown':
        ax.set_title(f'GRIDSAT-GOES Channel 4 Brightness Temperature IR | {str(hour).zfill(2)}:00 UTC {str(day).zfill(2)}/{str(month).zfill(2)}/{year}\n{s_ID} {storm_name} | {satellite[:-2].upper()}-{satellite[-2:]} | Max center temp = {kelvin_to_celsius(max_temp)} °C')
    else:
        ax.set_title(f'GRIDSAT B1 Brightness Temperature IR | {str(hour).zfill(2)}:00 UTC {str(day).zfill(2)}/{str(month).zfill(2)}/{year}\n{s_ID} {storm_name} | Max center temp = {kelvin_to_celsius(max_temp)} °C')
    gls = ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')
    gls.top_labels = False
    gls.right_labels = False
    gls.xlocator = mticker.FixedLocator(range(-180, 181, 2))  # Control gridline spacing
    gls.ylocator = mticker.FixedLocator(range(-90, 91, 2))
    #gl.xformatter = LONGITUDE_FORMATTER
    gls.yformatter = LATITUDE_FORMATTER
    gls.xlabel_style = {'size': 8, 'color': 'w'}  # Customize label style
    gls.ylabel_style = {'size': 8, 'color': 'w'}
    

    import matplotlib.ticker as ticker
    cbar = plt.colorbar(pcolor, label=f'Brightness Temperature (Celcius) | Colorscale: {cmap_func.__name__}')
    cbar.locator = ticker.MultipleLocator(10)
    cbar.update_ticks()

    plt.tight_layout()
    image_path = f'_SST_Map.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    async def send_image(image_path):
        with open(image_path, 'rb') as image_file:
            image = discord.File(image_file)
            await ctx.send(file=image)

    # Send the generated image
    await send_image(image_path)

    # Remove the temporary image file
    os.remove(image_path)

    dataset.close()
    os.remove(destination)

@bot.command(name='hodoplot')
async def hodoplot(ctx, btkID:str, yr:str, hour:int, day:int, month:int, year:int):
    import matplotlib.style as mplstyle
    import csv
    import cdsapi
    import xarray as xr
    import numpy as np
    import matplotlib.pyplot as plt
    from metpy.calc import wind_speed
    from metpy.plots import Hodograph
    from metpy.units import units
    import metpy.calc as mpcalc
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    import matplotlib.style as mplstyle
    import os
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    mplstyle.use("dark_background") 

    print(f"Command received from server: {ctx.guild.name}")
    btkID = btkID.upper()
    if btkID == 'BENTO':
        btkID = 'BENTOJANA'
    duplicates = ['ALICE 1953', 'ALICE 1954', 'ANA 2021', 'BABE 1977', 'BETTY 1966', 'BETTY 1972', 'BETTY 1975',
                  'DOREEN 1965', 'EDITH 1967', 'ELLEN 1973', 'FABIAN 1985', 'IDA 1972', 'IRMA 1978', 'IVY 1994',
                  'JUDY 1989', 'LINDA 1997', 'MAX 1981', 'NINA 1992', 'NORMAN 2000', 'ODETTE 2021', 'PAUL 2000',
                  'ROSE 1965', 'RUTH 1980', 'SALLY 1971', 'SARAH 1983', 'SHARON 1994', 'TIM 1994', 'WANDA 1974',
                  'TOMAS 2010', 'VICKY 2020', 'JOYCE 2018', 'GORDON 1979', 'BENI 2003', 'MARK 1992', 'NADINE 1978',
                  'WINNIE 1978', 'HARVEY 2005', 'FREDA 1981', 'POLLY 1971', 'LOUISE 1970', 'LUCY 1962', 'CARMEN 1974']
    check = f"{btkID} {yr}"
    if check in duplicates:
        await ctx.send(f"Error: {check} is the name of multiple storms in this database. Consider using their ATCF IDs instead.")
        return
    if(btkID == 'NOT_NAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    if(btkID == 'UNNAMED'):
        await ctx.send("Due to the IBTRACS database being ambiguous with this name, it cannot be used.")
        return
    
    def _00x_to_xx00(des):
        convert_map = {"L": "AL", "E": "EP", "C": "CP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}
        return convert_map[des[-1]] + des[:-1]

    import re
    if re.match(r"^\d{2}[A-Z]$", btkID):    
        btkID = _00x_to_xx00(btkID)

    #Load in the loops for finding the latitude and longitude...
    IBTRACS_ID = f"{btkID}{yr}"
    cdx, cdy, DateTime = 0, 0, ""
    storm_name = ""
    s_ID = ""
    idl = False
    await ctx.send("Please wait. Due to my terrible potato laptop, the dataset may take a while to go through.")
    #Template to read the IBTRACS Data...
    with open('ibtracs.ALL.list.v04r01.csv', mode='r') as file:
        csvFile = csv.reader(file)
        for line_num, lines in enumerate(csvFile, start=1):
            if line_num > 3:
                #Process or print the lines from the 4th line onwards
                #If IBTRACS ID matches the ID on the script...
                if lines[18] == IBTRACS_ID or (btkID == lines[5] and yr == lines[6][:4]):
                    DateTime = lines[6]
                    if int(DateTime[:4]) == year and int(DateTime[5:7]) == month and int(DateTime[8:10]) == day and int(DateTime[-8:-6]) == hour:
                        cdy, cdx = float(lines[19]), float(lines[20])
                        storm_name = lines[5]
                        break
    
    if cdx == 0:
        await ctx.send("Error 404: Storm not found. Please check if your entry is correct.")
        return

    await ctx.send("System located in database, generating API request...")

    lat, lon = cdy, cdx
    # === 1. Retrieve ERA5 Wind Data === #
    def retrieve_era5_hodograph(year, month, day, hour, lat_north, lon_west, lat_south, lon_east):
        client = cdsapi.Client()
        
        dataset = "reanalysis-era5-pressure-levels"
        request = {
            "product_type": "reanalysis",
            "variable": ["u_component_of_wind", "v_component_of_wind"],
            "pressure_level": ["1000", "950", "900", "850", "800", "750", "700", "650", "600", "550", "500", "450", "400", "350", "300" ,"250", "200", "150", "100"],  
            "year": str(year),
            "month": str(month).zfill(2),
            "day": str(day).zfill(2),
            "time": f"{hour}:00",
            "format": "netcdf",
            "area": [lat_north, lon_west, lat_south, lon_east],  # North, West, South, East
        }
        
        filename = "ERA5_hodograph.nc"
        client.retrieve(dataset, request, filename)
        return filename

    lat_north, lon_west, lat_south, lon_east = lat+2.5, lon-2.5, lat-2.5, lon+2.5  # Define 5×5 grid
    nc_file = retrieve_era5_hodograph(year, month, day, hour, lat_north, lon_west, lat_south, lon_east)
    await ctx.send("API Request to CDS successful, plotting values...")
    ds = xr.open_dataset(nc_file)
    
    # Debug: Print dataset info
    #print(ds)

    # Assign units using Pint accessor
    ds = ds.metpy.quantify()

    # Ensure wind components have correct units
    ds["u"] = ds["u"].metpy.convert_units("knots")
    ds["v"] = ds["v"].metpy.convert_units("knots")

    # Compute mean wind components
    u_wind = ds["u"].mean(dim=["latitude", "longitude"])
    v_wind = ds["v"].mean(dim=["latitude", "longitude"])

    # Extract pressure levels
    pressure_levels = ds["pressure_level"].metpy.convert_units("hPa")

    # === Create Hodograph Plot === #
    fig, ax = plt.subplots(figsize=(10, 10))
    date = f"{str(day).zfill(2)}/{str(month).zfill(2)}/{str(year)} at {str(hour).zfill(2)}00 UTC"
    ax.set_title(f"ECMWF ERAv5 plotted Hodograph for {btkID} {yr}\n{date}, 5x5° Area-Averaged Grid with calculated shear vectors", fontsize=7, fontweight="bold")

    # Hodograph setup
    max_wind = max(
    abs(u_wind.metpy.convert_units("knots").values.max()),
    abs(v_wind.metpy.convert_units("knots").values.max()),
    abs(u_wind.metpy.convert_units("knots").values.min()),
    abs(v_wind.metpy.convert_units("knots").values.min())
    )
    hodo = Hodograph(ax, component_range=max_wind + 5)
    hodo.add_grid(increment=10)  

    # Plotting wind data
    hodo.plot(u_wind, v_wind, marker="o", markersize=1, linestyle="-", color="b", label="Wind Profile")

    # Colormap based on pressure levels
    cmap = cm.get_cmap("Spectral_r")
    norm = mcolors.Normalize(vmin=pressure_levels.min(), vmax=pressure_levels.max())

    # Plotting wind data with colored lines and black points
    for i in range(len(pressure_levels) - 1):
        u1, v1 = u_wind.isel(pressure_level=i).values.item(), v_wind.isel(pressure_level=i).values.item()
        u2, v2 = u_wind.isel(pressure_level=i+1).values.item(), v_wind.isel(pressure_level=i+1).values.item()
        
        # Colored line segment
        ax.plot([u1, u2], [v1, v2], color=cmap(norm(pressure_levels[i].values)), linewidth=2)

    for i, level in enumerate(ds["pressure_level"].values):
        if level in [850, 700, 500, 350, 200]:  # Relevant pressure values
            u_value = u_wind.isel(pressure_level=i).values.item()
            v_value = v_wind.isel(pressure_level=i).values.item()
            
            ax.scatter(u_value, v_value, s=30, edgecolor="white", linewidth=0.7, zorder=10000)
            ax.text(
                u_value,
                v_value,
                f"{level:.0f} hPa",
                fontsize=10,
                ha="center"
            )

    # Create a divider for the axis to position the colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)  # Adjust size and padding

    # Add colorbar 
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cax, orientation="vertical", label="Pressure Level (hPa)")
    ax.set_xlabel("U-wind (m/s)", fontsize=12)
    ax.set_ylabel("V-wind (m/s)", fontsize=12)

    # === Compute and Plot Shear Vectors === #
    shear_layers = {
        "200–850 hPa": (200, 850),
        "500–850 hPa": (500, 850),
        "200–500 hPa": (200, 500),
        "300–800 hPa": (300, 800),
        "850–1000 hPa": (850, 1000),
    }

    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyArrowPatch
    from matplotlib.legend_handler import HandlerPatch
    from matplotlib.lines import Line2D
    
    class HandlerArrow(HandlerPatch):
        def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
            # Calculate the center of the arrow
            center = height / 2.0

            # Use a valid color (e.g., white) explicitly
            color = "white"

            # Create the FancyArrowPatch for the legend
            p = FancyArrowPatch(
                (xdescent + width * 0.2, center),  # Start point
                (xdescent + width * 0.8, center),  # End point
                mutation_scale=15,  # Scale of arrow
                color=color,         # Explicitly set valid color
                arrowstyle="->"      # Define arrow style explicitly
            )
            p.set_transform(trans)
            return [p]
    max_shear = 0

    legend_elements = []

    arrow_length_display = 10  # fixed visual arrow length
    arrow_color = "white"

    for label, (lower, upper) in shear_layers.items():
        u_lower = u_wind.sel(pressure_level=lower).values.item()
        v_lower = v_wind.sel(pressure_level=lower).values.item()
        u_upper = u_wind.sel(pressure_level=upper).values.item()
        v_upper = v_wind.sel(pressure_level=upper).values.item()

        shear_u = u_upper - u_lower
        shear_v = v_upper - v_lower
        shear_mag = np.sqrt(shear_u**2 + shear_v**2)

        ax.quiver(
        u_lower, v_lower,    # Starting point (lower pressure level)
        shear_u, shear_v,    # Components (direction and magnitude)
        angles="xy", scale_units="xy", scale=1, color="#808080", width=0.002, linestyle="--"
        )

        # Normalize for fixed arrow direction
        unit_u = shear_u / shear_mag
        unit_v = shear_v / shear_mag

        scaled_u = unit_u * arrow_length_display
        scaled_v = unit_v * arrow_length_display

        # Create a custom arrow legend handle
        arrow = FancyArrowPatch(
            (0, 0), (shear_u, shear_v),  # unit direction
            color="white",
            arrowstyle='->',
            mutation_scale=15,
            lw=2
        )
        legend_elements.append(
            (arrow, f"{label}: {shear_mag:.1f} kt")
        )
    
    #Max shear calculation:
    upper, lower = ["200", "250", "300", "350", "400", "450", "500"], ["700", "750", "800", "850", "900"]
    maxUpper, maxLower = "", ""
    maxShear = 0
    for u in upper:
        for l in lower:
            u_lower = u_wind.sel(pressure_level=l).values.item()
            v_lower = v_wind.sel(pressure_level=l).values.item()
            u_upper = u_wind.sel(pressure_level=u).values.item()
            v_upper = v_wind.sel(pressure_level=u).values.item()

            shear_u = u_upper - u_lower
            shear_v = v_upper - v_lower
            shear_mag = np.sqrt(shear_u**2 + shear_v**2)

            if shear_mag > maxShear:
                maxShear = shear_mag
                maxUpper = u
                maxLower = l
            
    legend_elements.append(
            (arrow, f"Max shear: {maxShear:.1f} kt ({maxUpper}-{maxLower} hPa)")
        )
    # Unpack handles and labels
    handles, labels = zip(*legend_elements)
    ax.legend(
        handles, labels,
        loc="lower center",
        fontsize=8,
        frameon=True,
        ncol=2,
        handler_map={FancyArrowPatch: HandlerArrow()}
    )

    image_path = f'Hodograph.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)
    os.remove(image_path)

@bot.command(name='hodoplot_custom')
async def hodoplot_custom(ctx, lat:float, lon:float, hour, day, month, year, gridres=5):
    import cdsapi
    import xarray as xr
    import numpy as np
    import matplotlib.pyplot as plt
    from metpy.calc import wind_speed
    from metpy.plots import Hodograph
    from metpy.units import units
    import metpy.calc as mpcalc
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    import matplotlib.style as mplstyle
    import os
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    mplstyle.use("dark_background") 
    await ctx.send("Please be patient as the required data is plotted.")

    # === 1. Retrieve ERA5 Wind Data === #
    def retrieve_era5_hodograph(year, month, day, hour, lat_north, lon_west, lat_south, lon_east):
        client = cdsapi.Client()
        
        dataset = "reanalysis-era5-pressure-levels"
        request = {
            "product_type": "reanalysis",
            "variable": ["u_component_of_wind", "v_component_of_wind"],
            "pressure_level": ["1000", "950", "900", "850", "800", "750", "700", "650", "600", "550", "500", "450", "400", "350", "300" ,"250", "200", "150", "100"],  
            "year": str(year),
            "month": str(month).zfill(2),
            "day": str(day).zfill(2),
            "time": f"{hour}:00",
            "format": "netcdf",
            "area": [lat_north, lon_west, lat_south, lon_east],  # North, West, South, East
        }
        
        filename = "ERA5_hodograph.nc"
        client.retrieve(dataset, request, filename)
        return filename

    lat_north, lon_west, lat_south, lon_east = lat+(gridres/2), lon-(gridres/2), lat-(gridres/2), lon+(gridres/2)  # Define grid
    nc_file = retrieve_era5_hodograph(year, month, day, hour, lat_north, lon_west, lat_south, lon_east)
    await ctx.send("API Request to CDS successful, plotting values...")
    ds = xr.open_dataset(nc_file)
    
    # Debug: Print dataset info
    #print(ds)

    # Assign units using Pint accessor
    ds = ds.metpy.quantify()

    # Ensure wind components have correct units
    ds["u"] = ds["u"].metpy.convert_units("knots")
    ds["v"] = ds["v"].metpy.convert_units("knots")

    # Compute mean wind components
    u_wind = ds["u"].mean(dim=["latitude", "longitude"])
    v_wind = ds["v"].mean(dim=["latitude", "longitude"])

    # Extract pressure levels
    pressure_levels = ds["pressure_level"].metpy.convert_units("hPa")

    # === Create Hodograph Plot === #
    fig, ax = plt.subplots(figsize=(10, 10))
    date = f"{str(day).zfill(2)}/{str(month).zfill(2)}/{str(year)} at {str(hour).zfill(2)}00 UTC"
    ax.set_title(f"ECMWF ERAv5 plotted Hodograph centered over ({lat}, {lon})\n{date}, 5x5° Area-Averaged Grid with calculated shear vectors", fontsize=7, fontweight="bold")

    # Hodograph setup
    max_wind = max(
    abs(u_wind.metpy.convert_units("knots").values.max()),
    abs(v_wind.metpy.convert_units("knots").values.max()),
    abs(u_wind.metpy.convert_units("knots").values.min()),
    abs(v_wind.metpy.convert_units("knots").values.min())
    )
    hodo = Hodograph(ax, component_range=max_wind + 5)
    hodo.add_grid(increment=10)  

    # Plotting wind data
    hodo.plot(u_wind, v_wind, marker="o", markersize=1, linestyle="-", color="b", label="Wind Profile")

    # Colormap based on pressure levels
    cmap = cm.get_cmap("Spectral_r")
    norm = mcolors.Normalize(vmin=pressure_levels.min(), vmax=pressure_levels.max())

    # Plotting wind data with colored lines and black points
    for i in range(len(pressure_levels) - 1):
        u1, v1 = u_wind.isel(pressure_level=i).values.item(), v_wind.isel(pressure_level=i).values.item()
        u2, v2 = u_wind.isel(pressure_level=i+1).values.item(), v_wind.isel(pressure_level=i+1).values.item()
        
        # Colored line segment
        ax.plot([u1, u2], [v1, v2], color=cmap(norm(pressure_levels[i].values)), linewidth=2)

    for i, level in enumerate(ds["pressure_level"].values):
        if level in [850, 700, 500, 350, 200]:  # Relevant pressure values
            u_value = u_wind.isel(pressure_level=i).values.item()
            v_value = v_wind.isel(pressure_level=i).values.item()
            
            ax.scatter(u_value, v_value, s=30, edgecolor="white", linewidth=0.7, zorder=10000)
            ax.text(
                u_value,
                v_value,
                f"{level:.0f} hPa",
                fontsize=10,
                ha="center"
            )

    # Create a divider for the axis to position the colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)  # Adjust size and padding

    # Add colorbar 
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cax, orientation="vertical", label="Pressure Level (hPa)")
    ax.set_xlabel("U-wind (knots)", fontsize=12)
    ax.set_ylabel("V-wind (knots)", fontsize=12)

    # === Compute and Plot Shear Vectors === #
    shear_layers = {
        "200–850 hPa": (200, 850),
        "500–850 hPa": (500, 850),
        "200–500 hPa": (200, 500),
        "300–800 hPa": (300, 800),
        "850–1000 hPa": (850, 1000),
    }

    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyArrowPatch
    from matplotlib.legend_handler import HandlerPatch
    from matplotlib.lines import Line2D
    max_shear = []
    class HandlerArrow(HandlerPatch):
        def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
            # Calculate the center of the arrow
            center = height / 2.0

            # Use a valid color (e.g., white) explicitly
            color = "white"

            # Create the FancyArrowPatch for the legend
            p = FancyArrowPatch(
                (xdescent + width * 0.2, center),  # Start point
                (xdescent + width * 0.8, center),  # End point
                mutation_scale=15,  # Scale of arrow
                color=color,         # Explicitly set valid color
                arrowstyle="->"      # Define arrow style explicitly
            )
            p.set_transform(trans)
            return [p]


    legend_elements = []

    arrow_length_display = 10  # fixed visual arrow length
    arrow_color = "white"

    for label, (lower, upper) in shear_layers.items():
        u_lower = u_wind.sel(pressure_level=lower).values.item()
        v_lower = v_wind.sel(pressure_level=lower).values.item()
        u_upper = u_wind.sel(pressure_level=upper).values.item()
        v_upper = v_wind.sel(pressure_level=upper).values.item()

        shear_u = u_upper - u_lower
        shear_v = v_upper - v_lower
        shear_mag = np.sqrt(shear_u**2 + shear_v**2)

        ax.quiver(
        u_lower, v_lower,    # Starting point (lower pressure level)
        shear_u, shear_v,    # Components (direction and magnitude)
        angles="xy", scale_units="xy", scale=1, color="#808080", width=0.002, linestyle="--"
        )

        # Normalize for fixed arrow direction
        unit_u = shear_u / shear_mag
        unit_v = shear_v / shear_mag

        scaled_u = unit_u * arrow_length_display
        scaled_v = unit_v * arrow_length_display

        # Create a custom arrow legend handle
        arrow = FancyArrowPatch(
            (0, 0), (shear_u, shear_v),  # unit direction
            color="white",
            arrowstyle='->',
            mutation_scale=15,
            lw=2
        )
        legend_elements.append(
            (arrow, f"{label}: {shear_mag:.1f} kt")
        )
    #Max shear calculation:
    upper, lower = ["200", "250", "300", "350", "400", "450", "500"], ["700", "750", "800", "850", "900"]
    maxUpper, maxLower = "", ""
    maxShear = 0
    for u in upper:
        for l in lower:
            u_lower = u_wind.sel(pressure_level=l).values.item()
            v_lower = v_wind.sel(pressure_level=l).values.item()
            u_upper = u_wind.sel(pressure_level=u).values.item()
            v_upper = v_wind.sel(pressure_level=u).values.item()

            shear_u = u_upper - u_lower
            shear_v = v_upper - v_lower
            shear_mag = np.sqrt(shear_u**2 + shear_v**2)

            if shear_mag > maxShear:
                maxShear = shear_mag
                maxUpper = u
                maxLower = l
            
    legend_elements.append(
            (arrow, f"Max shear: {maxShear:.1f} kt ({maxUpper}-{maxLower} hPa)")
        )
    # Unpack handles and labels
    handles, labels = zip(*legend_elements)
    ax.legend(
        handles, labels,
        loc="lower center",
        fontsize=8,
        frameon=True,
        ncol=2,
        handler_map={FancyArrowPatch: HandlerArrow()}
    )

    image_path = f'Hodograph.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)
    os.remove(image_path)

@bot.command(name='windplot')
async def windplot(ctx, pres:str, hour:str, day:str, month:str, year:str, areaN=90, areaS=-90, areaW=-180, areaE=180, color='jet'):
    import cdsapi
    import cfgrib
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import os

    await ctx.send("Please be patient as the required data is plotted.")

    # Step 1: Download the data using the CDS API
    dataset = "reanalysis-era5-pressure-levels"
    request = {
        'product_type': ['reanalysis'],
        'variable': ['u_component_of_wind', 'v_component_of_wind'],
        'year': [f'{year}'],
        'month': [f'{month.zfill(2)}'],
        'day': [f'{day.zfill(2)}'],
        'time': [f'{hour.zfill(2)}:00'],
        'pressure_level': [f'{pres}'],
        'format': 'grib',
        'area': [areaN, areaW, areaS, areaE]  # North, West, South, East
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request).download('download.grib')
    await ctx.send("API Request to CDS successful, plotting values...")
    # Step 2: Read and process the GRIB data
    ds = cfgrib.open_dataset('download.grib')
    u850_data = ds['u'].values
    v850_data = ds['v'].values
    
    lats = ds['latitude'].values
    lons = ds['longitude'].values
    

    # Step 3: Plot the streamlines with color representing wind speed in knots
    
    # Calculate wind speed magnitude in m/s
    wind_speed_m_s = np.sqrt(u850_data**2 + v850_data**2)
    # Convert wind speed to knots
    wind_speed_knots = wind_speed_m_s * 1.94384
    
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    ax.set_extent([areaW, areaE, areaS, areaN], crs=ccrs.PlateCarree())
    
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.LAND, edgecolor='black')
    
    # Add grid lines
    ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    
    # Plot streamlines with color representing wind speed
    strm = ax.streamplot(lons, lats, u850_data, v850_data, transform=ccrs.PlateCarree(), linewidth=1, density=2,
                        color=wind_speed_knots, cmap=f'{color}', arrowstyle='->', arrowsize=1.5)
    
    # Add a color bar, scaled to fit the plot size
    cbar = plt.colorbar(strm.lines, ax=ax, orientation='horizontal', pad=0.05, aspect=50, shrink=0.5)
    cbar.set_label('Wind Speed (m/s)')
    
    plt.title(f'ERA5 Reanalysis Streamlines of Winds at {pres} hPa\n {hour.zfill(2)}00 UTC on {day.zfill(2)}/{month.zfill(2)}/{year}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.tight_layout()
    # Adjust spacing above and below the plot
    
    image_path = f'Streamlines.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)
    os.remove(image_path)

@bot.command(name='reconplot')
async def reconplot(ctx, basin:str, aircraftType:str):
    import urllib3
    from bs4 import BeautifulSoup
    import re
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    from datetime import datetime
    import matplotlib.colors as mcolors
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    import matplotlib.transforms as transforms
    import math
    import os
    import matplotlib.style as mplstyle

    mplstyle.use("dark_background") 
    await ctx.send("Please be patient as the data is plotted.")
    basin = basin.upper()
    aircraftType = aircraftType.upper()

    basinHDOB = {'ATL':'URNT15', 'EPAC':'URPN15', 'WPAC':'URPA15'}

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)

    def fetch_url(urlLink):
        response = http.request('GET', urlLink)
        return response.data.decode('utf-8')

    def parse_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    url = f"https://www.nhc.noaa.gov/text/{basinHDOB[basin]}-{aircraftType}.shtml?text"
    btk_data = fetch_url(url)
    parsed_data = parse_data(btk_data)

    lines = parsed_data.split('\n')

    def is_three_digit_number(s):
        pattern = r'^(?!.*\|)\d{3}$'
        return bool(re.match(pattern, s))

    validData = []
    isValidData = 0

    for line in lines:
        line = line.strip()  # This removes any extra spaces from the line
        if line:
            if line == "$$" or line.split()[0] == "Standard":
                isValidData = 0
                break
            if is_three_digit_number(line) or line == '000':
                isValidData = 1
            if isValidData == 1:
                validData.append(line)  # Only add valid data lines to the list
                
        reconHDOB = []
        for i in range(12, len(validData)):  
            reconHDOB.append(validData[i])

    for i in range(len(reconHDOB)):
        print(reconHDOB[i])

    # Create the plot and set up the map
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    ax.coastlines()
    ax.gridlines(draw_labels=True, linewidth=0.5, linestyle='--', color='gray')

    # Define the color mapping for wind speeds
    colors = ['b', 'g', '#ffff00', '#ffa001', '#ff5908', 'r', 'm']
    bounds = [0, 34, 64, 81, 96, 112, 137, 200]
    norm = mcolors.BoundaryNorm(bounds, len(colors))

    def plot_wind_barb(ax, wind_speed, wind_direction, lat, lon, xtrap_val=0, sfmr='', flag=0):
        # Convert wind direction to radians
        wind_direction_rad = np.radians(wind_direction)
        
        # Calculate the u and v components of the wind vector
        u = wind_speed * np.sin(wind_direction_rad)
        v = wind_speed * np.cos(wind_direction_rad)
        
        if wind_speed >= 137:
            color = 'm'
        elif wind_speed >= 112:
            color = 'r'
        elif wind_speed >= 96:
            color = '#ff5908'
        elif wind_speed >= 81:
            color = '#ffa001'
        elif wind_speed >= 64:
            color = '#ffff00'
        elif wind_speed >= 34:
            color = 'g'
        else:
            color = 'b'

        # Plot the wind barb on the existing map
        ax.barbs(lon, lat, u, v, length=7, color=color, transform=ccrs.PlateCarree())
        ax.text(lon, lat+0.01, f'{int(wind_speed)} FL/{sfmr} SFC\n{xtrap_val}', transform=ccrs.PlateCarree(), fontsize=8, ha='center', va='center')
        if sfmr != '' and flag==1:
            ax.text(lon, lat, '!', color='r', transform=ccrs.PlateCarree(), fontsize=15, ha='center', va='center')

    maxLat, minLat, maxLong, minLong = -999, 999, -999, 999
    for data_line in reconHDOB:
        HDOBfix = data_line.split()
        print(HDOBfix)

        lat = float(HDOBfix[1][:2]) + float(HDOBfix[1][2:4])/60
        lon = float(HDOBfix[2][:3]) + float(HDOBfix[2][3:5])/60
        if HDOBfix[1][-1] == 'S':
            lat *= -1
        if HDOBfix[2][-1] == 'W':
            lon *= -1

        if(maxLat < lat):
            maxLat = lat
        if(minLat > lat):
            minLat = lat
        if(maxLong < lon):
            maxLong = lon
        if(minLong > lon):
            minLong = lon 
        
        fl_wind_dir = ( float(HDOBfix[8][:3])) + 180
        fl_wind_speed=''
        if fl_wind_speed == "///":
            continue

        fl_wind_speed = float(HDOBfix[9])

        sfmr = HDOBfix[10]
        print(sfmr)
        if sfmr == '///':
            sfmr = 'NaN'
        else:
            sfmr = int(sfmr)

        xtrap = HDOBfix[5]
        xtrap_val = 0
        if xtrap == '////':
            xtrap_val = ''
        elif xtrap[0] == '0':
            xtrap_val = 1000 + float(xtrap)/10
        else:
            xtrap_val = float(xtrap)/10

        flag=0
        if HDOBfix[-1][-1] in ['5', '6', '9']:
            flag=1
        print(lat, ", ", lon, ", ", fl_wind_dir, ", ", fl_wind_speed)
        
        plot_wind_barb(ax, fl_wind_speed, fl_wind_dir, lat, lon, xtrap_val, sfmr, flag)

    def calculate_bearing(lat1, lon1, lat2, lon2):
        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)
        
        # Calculate the difference in longitude
        d_lon = lon2 - lon1
        
        # Calculate the bearing
        x = math.sin(d_lon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(d_lon))
        initial_bearing = math.atan2(x, y)
        
        # Convert bearing from radians to degrees
        initial_bearing = math.degrees(initial_bearing)
        
        # Normalize the bearing
        bearing = (initial_bearing + 360) % 360
        
        return bearing + 180

    second_last = reconHDOB[-2].split()
    seclast_lat = (float(second_last[1][:2]) + float(second_last[1][2:4])/60)
    seclast_lat = seclast_lat*-1 if second_last[1][-1] == 'S' else seclast_lat
    seclast_lon = (float(second_last[2][:3]) + float(second_last[2][3:5])/60)
    seclast_lon = seclast_lon*-1 if second_last[2][-1] == 'W' else seclast_lon

    plane_Loc = reconHDOB[-1].split()
    plane_lat = (float(plane_Loc[1][:2]) + float(plane_Loc[1][2:4])/60)
    plane_lat = plane_lat*-1 if plane_Loc[1][-1] == 'S' else plane_lat
    plane_lon = (float(plane_Loc[2][:3]) + float(plane_Loc[2][3:5])/60)
    plane_lon = plane_lon*-1 if plane_Loc[2][-1] == 'W' else plane_lat

    degrees = calculate_bearing(seclast_lat, seclast_lon, plane_lat, plane_lon)

    rotation = transforms.Affine2D().rotate_deg(degrees)
    # Combine the rotation transformation with the current plot's transformation
    transform = rotation + ax.transData

    ax.plot(lon, lat, marker=(3, 0, degrees), markersize=10, transform=ax.transData, linestyle='None', color='w')

    legend_elements = [Line2D([0], [0], marker='^', color='w', label='Last reported Aircaft Location & Direction Bearing', markerfacecolor='#444764', markersize=10),]

    ax.set_extent([minLong-0.05, maxLong+0.05, minLat-0.05, maxLat+0.05], crs=ccrs.PlateCarree())

    # Get the current UTC time
    current_utc_time = datetime.utcnow()

    plt.title(f'Recon Flight Data from {aircraftType} as of {current_utc_time} UTC')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Create the colorbar
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    ax.legend(handles=legend_elements, loc='upper center')

    # Add colorbar to the plot
    cbar = plt.colorbar(sm, ticks=bounds, orientation='horizontal', pad=0.05, aspect=50, ax=ax, shrink=0.5)
    cbar.set_label('30-sec recorded FL wind speed (Knots)')
    cbar.ax.set_xticklabels(['0', '34', '64', '81', '96', '112', '137', '200'])

    plt.tight_layout()
    
    r = np.random.randint(1, 10)
    image_path = f'Recon_Map{r}.png'
    plt.savefig(image_path, format='png', bbox_inches='tight')
    plt.close()

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

    os.remove(image_path)  

@bot.command(name='tcprimed')
async def tcprimed(ctx):
    await ctx.send("https://colab.research.google.com/drive/18jAoFVesVHu6cYzfL7Jk7mY0GEHnzqyY?usp=sharing")

@bot.command(name='hursat_avhrr')
async def hursat_avhrr(ctx):
    await ctx.send("https://colab.research.google.com/drive/1m27IzsuwQyyLmNSkkI9VtDIkBAePkBiZ?usp=sharing")

@bot.command(name='hursat_b1')
async def hursat_b1(ctx):
    await ctx.send("https://colab.research.google.com/drive/1Rgjwg3-Fd_ce17BZnyBp8gCRe5DGrkOx?usp=sharing")

@bot.command(name='land_degrade')
async def land_degrade(ctx, v0:float, hour:float, us=0):
    import math
    v_t = v0 * math.exp(-0.044 * hour) if us == 0 else v0 * math.exp(-0.08 * hour)
    v_t = "{:.2f}".format(v_t)
    await ctx.send(f"The extrapolated intensity {hour} hour(s) post landfall: {v_t} Kt")

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

@bot.command(name='batsirai')
async def batsirai(ctx):
    image_path1 = 'batsirai.webp'

    with open(image_path1, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='megaslop')
async def megaslop(ctx):
    image_path1 = 'gfsmegalop.webp'

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

@bot.command(name='rulef')
async def rulef(ctx):
    image_path = 'rulef.webp'

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

@bot.command(name='mangkhut')
async def mangkhut(ctx):
    image_path = 'mangkhut.gif'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command('weaktight')
async def weaktight(ctx):
    image_path = 'hinnafail.webp'
    await ctx.send("```ANIMATED MULTISPECTRAL SATELLITE IMAGERY (MSI) SHOWS A"+ 
    " MORE CONSOLIDATED AREA OF CONVECTION WRAPPING INTO A MID-LEVEL "+
    "ROTATION. HOWEVER, THIS SYSTEM IS VOID OF A LOW LEVEL CIRCULATION "+
    "CENTER AND HAS A WEAK BUT TIGHT TROUGHING ASSOCIATED WITH A WAVE "+
    "PROPAGATING NORTHWESTWARD. THIS TIGHT TROUGH IS EVIDENT ON THE 272330Z "+
    "PARTIAL ASCAT-C PASS.```")
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

@bot.command(name='bumrah')
async def bumrah(ctx):
    image_path = 'bumrahxpope-bumrah.mp4'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='erick')
async def erick(ctx):
    image_path = 'Erick.PNG'

    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)

@bot.command(name='look')
async def erick(ctx):
    image_path = 'thelook.webp'

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

@bot.command(name='errol')
async def errol(ctx):
    image_path = 'errol_bom.webp'
    image_path2 = 'errol_bom2.webp'
    with open(image_path, 'rb') as image_file:
        image = discord.File(image_file)
        await ctx.send(file=image)
    with open(image_path2, 'rb') as image_file:
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

@bot.command(name='front')
async def front(ctx):
    image_path = 'front.webp'

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

bot.run(AUTH_TOKEN)

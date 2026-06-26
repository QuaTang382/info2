import nextcord
from nextcord.ext import commands
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

intents = nextcord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Danh sách các region
REGIONS = ["IND", "BR", "SG", "RU", "ID", "TW", "US", "VN", "TH", "ME", "PK", "CIS", "BD", "NA", "SAC", "EU"]

@bot.slash_command(name="info", description="Lấy thông tin người chơi Free Fire")
async def info(interaction: nextcord.Interaction,
               uid: str = nextcord.SlashOption(description="ID tài khoản Free Fire"),
               region: str = nextcord.SlashOption(description="Khu vực", choices=REGIONS)):
    await interaction.response.defer()

    api_url = f"https://dark-aura-info-api-v1-main.vercel.app/player-info?region={region}&uid={uid}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, timeout=10) as response:
                if response.status != 200:
                    await interaction.followup.send(f"❌ Lỗi: Status {response.status}")
                    return

                data = await response.json()

                if "error" in data:
                    await interaction.followup.send(f"❌ Lỗi: {data['error']}")
                    return

                # Tạo embed
                embed = nextcord.Embed(
                    title=f"🎮 Thông tin người chơi {data['basicInfo']['nickname']}",
                    description=f"Khu vực: **{data['basicInfo']['region']}**",
                    color=nextcord.Color.gold()
                )

                basic = data['basicInfo']
                embed.add_field(
                    name="📋 Thông tin cơ bản",
                    value=(
                        f"**UID:** {basic['accountId']}\n"
                        f"**Nickname:** {basic['nickname']}\n"
                        f"**Level:** {basic['level']}\n"
                        f"**EXP:** {basic['exp']:,}\n"
                        f"**Lượt thích:** {basic['liked']:,}\n"
                        f"**Huy hiệu:** {basic['badgeCnt']}\n"
                        f"**Mùa giải:** {basic['seasonId']}\n"
                        f"**Tạo lúc:** <t:{basic['createAt']}:R>"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="🏆 Xếp hạng",
                    value=(
                        f"**BR Rank:** {basic['rank']}\n"
                        f"**BR Điểm:** {basic['rankingPoints']}\n"
                        f"**CS Rank:** {basic['csRank']}\n"
                        f"**CS Điểm:** {basic['csRankingPoints']}\n"
                        f"**BR Cao nhất:** {basic['maxRank']}\n"
                        f"**CS Cao nhất:** {basic['csMaxRank']}"
                    ),
                    inline=True
                )

                if 'clanBasicInfo' in data and data['clanBasicInfo']:
                    clan = data['clanBasicInfo']
                    embed.add_field(
                        name="🏰 Clan",
                        value=(
                            f"**Tên:** {clan['clanName']}\n"
                            f"**ID:** {clan['clanId']}\n"
                            f"**Level:** {clan['clanLevel']}\n"
                            f"**Thành viên:** {clan['memberNum']}/{clan['capacity']}"
                        ),
                        inline=True
                    )

                if 'petInfo' in data and data['petInfo']:
                    pet = data['petInfo']
                    embed.add_field(
                        name="🐾 Thú cưng",
                        value=(
                            f"**Tên:** {pet['name']}\n"
                            f"**Level:** {pet['level']}\n"
                            f"**EXP:** {pet['exp']:,}"
                        ),
                        inline=True
                    )

                embed.add_field(
                    name="📝 Khác",
                    value=(
                        f"**Đăng nhập lần cuối:** <t:{basic['lastLoginAt']}:R>\n"
                        f"**Tín dụng:** {data.get('creditScoreInfo', {}).get('creditScore', 'N/A')}\n"
                        f"**Chữ ký:** {data.get('socialInfo', {}).get('signature', 'Không có')}"
                    ),
                    inline=False
                )

                embed.set_footer(text=f"Yêu cầu bởi {interaction.user.display_name}")
                embed.timestamp = nextcord.utils.utcnow()

                await interaction.followup.send(embed=embed)

        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Hết thời gian chờ. Thử lại nhé!")
        except aiohttp.ClientError:
            await interaction.followup.send("❌ Lỗi kết nối API!")
        except Exception as e:
            await interaction.followup.send(f"❌ Lỗi: {str(e)}")

@bot.event
async def on_ready():
    await bot.sync_application_commands()
    print(f'✅ Bot đã sẵn sàng! Tên: {bot.user}')

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Lỗi: Không tìm thấy DISCORD_TOKEN!")
        exit(1)
    bot.run(token)

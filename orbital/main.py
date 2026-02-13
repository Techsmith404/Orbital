#IMPORTS
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from sparklines import sparklines
from rich.live import Live
from rich import print
import psutil
import time
import subprocess

def main():
    #VARIABLES
    netStats = psutil.net_io_counters()
    netSentOld = netStats.bytes_sent
    netRecvOld = netStats.bytes_recv
    sentHistory = [0] * 30
    recvHistory = [0] * 30
    layout = Layout()
    headPan = Panel("Orbital", style="bold white on blue")
    reactorPan = Panel(Text.from_markup("[bold red]Reactor information goes here[/bold red]", justify="center"))
    thrusterPan = Panel(Text.from_markup("[bold green]Thruster information goes here[/bold green]", justify="center"))
    cargoPan = Panel(Text.from_markup("[bold yellow]Cargo information goes here[/bold yellow]", justify="center"))
    uplinkPan = Panel(Text.from_markup("[bold cyan]Uplink information goes here[/bold cyan]", justify="center"))

    #FUNCTIONS
    def gpuStats():
        try:
            gpuAll = subprocess.check_output(["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu", "--format=csv,noheader,nounits"])
            gpuAll = gpuAll.decode("utf-8").strip()
            temp, util = gpuAll.split(", ")
            return int(temp), int(util)
        except:
            return 0,0

    #LAYOUT CONFIGURATION
    layout.split_column(
        Layout(name="head", size=3),
        Layout(name="body")
    )

    layout["body"].split_row(
        Layout(name="bodyLeft"),
        Layout(name="bodyRight")
        )

    layout["bodyLeft"].split_column(
        Layout(name="topLeft"),
        Layout(name="bottomLeft")
        )

    layout["bodyRight"].split_column(
        Layout(name="topRight"),
        Layout(name="bottomRight")
        )

    #UPDATES
    layout["head"].update(headPan)
    layout["topLeft"].update(reactorPan)
    layout["topRight"].update(thrusterPan)
    layout["bottomLeft"].update(cargoPan)
    layout["bottomRight"].update(uplinkPan)

    #PRINT
    try:
        with Live(layout, refresh_per_second=2) as live:
            while True:
                #VARIABLES
                cpuPercent = psutil.cpu_percent(interval=0)
                memInfo = psutil.virtual_memory()
                diskInfo = psutil.disk_usage('/')
                disk2Info = psutil.disk_usage('/run/media/codaine/D05EF5A55EF5848E')
                netStats = psutil.net_io_counters()
                netSentNew = netStats.bytes_sent
                netRecvNew = netStats.bytes_recv
                gpuTemp, gpuUtil = gpuStats()

                #LOGIC
                sentSpeed = netSentNew - netSentOld
                recvSpeed = netRecvNew - netRecvOld
                netSentOld = netSentNew
                netRecvOld = netRecvNew

                sentHistory.pop(0)
                sentHistory.append(sentSpeed)
                recvHistory.pop(0)
                recvHistory.append(recvSpeed)

                obSpark = "".join(sparklines(sentHistory))
                ibSpark = "".join(sparklines(recvHistory))

                #PANEL UPDATES
                reactorPan = Panel(Text.from_markup(f"[bold red]Reactor is running at[/bold red] [bold underline yellow]{cpuPercent}%[/bold underline yellow] [bold red]capacity.[/bold red]", justify="center"))
                thrusterPan = Panel(Text.from_markup(f"[bold green]Thrusters temp is at [/bold green][bold underline yellow]{gpuTemp}[/bold underline yellow] [bold green]degrees under [/bold green][bold underline yellow]{gpuUtil}%[/bold underline yellow] [bold green]load[/bold green]", justify="center"))
                cargoPan = Panel(Text.from_markup(f"[bold yellow]Primary cargo hold is[/bold yellow] [bold underline red]{diskInfo.percent}%[/bold underline red] [bold yellow]full.[/bold yellow]\n[bold yellow]Secondary cargo hold is[/bold yellow] [bold underline red]{disk2Info.percent}%[/bold underline red] [bold yellow]full.[/bold yellow]\n[bold yellow]Random cargo hold is[/bold yellow] [bold underline red]{memInfo.percent}%[/bold underline red] [bold yellow]full.[/bold yellow]", justify="center"))
                uplinkPan = Panel(
                    Text.assemble(
                        ("Outbound:", "bold underline blue"), " ", (obSpark, "green"), (f" {sentSpeed / 1024:.1f} KB/s\n\n", "bold blue"),
                        ("Inbound:", "bold underline blue"), " ", (ibSpark, "purple"), (f" {recvSpeed / 1024:.1f} KB/s", "bold blue")
                        )
                    )

                #LIVE UPDATES
                layout["topLeft"].update(reactorPan)
                layout["topRight"].update(thrusterPan)
                layout["bottomLeft"].update(cargoPan)
                layout["bottomRight"].update(uplinkPan)

                time.sleep(1)
                pass
    except KeyboardInterrupt:
        print("\n[bold red]Orbital Systems Offline.[/bold red]")

if __name__ == "__main__":
    main()






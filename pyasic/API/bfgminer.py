# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

import logging

from pyasic.API import APIError, BaseMinerAPI


class BFGMinerAPI(BaseMinerAPI):
    """An abstraction of the BFGMiner API.

    Each method corresponds to an API command in BFGMiner.

    [BFGMiner API documentation](https://github.com/luke-jr/bfgminer/blob/bfgminer/README.RPC)

    This class abstracts use of the BFGMiner API, as well as the
    methods for sending commands to it.  The self.send_command()
    function handles sending a command to the miner asynchronously, and
    as such is the base for many of the functions in this class, which
    rely on it to send the command for them.

    Parameters:
        ip: The IP of the miner to reference the API on.
        port: The port to reference the API on.  Default is 4028.
    """

    def __init__(self, ip: str, api_ver: str = "0.0.0", port: int = 4028):
        super().__init__(ip, port)
        self.api_ver = api_ver

    async def multicommand(self, *commands: str, allow_warning: bool = True) -> dict:
        # make sure we can actually run each command, otherwise they will fail
        commands = self._check_commands(*commands)
        # standard multicommand format is "command1+command2"
        # doesn't work for S19 which uses the backup _x19_multicommand
        command = "+".join(commands)
        try:
            data = await self.send_command(command, allow_warning=allow_warning)
        except APIError:
            logging.debug(f"{self} - (Multicommand) - Handling X19 multicommand.")
            data = await self._x19_multicommand(*command.split("+"))
        data["multicommand"] = True
        return data

    async def _x19_multicommand(self, *commands) -> dict:
        data = None
        try:
            data = {}
            # send all commands individually
            for cmd in commands:
                data[cmd] = []
                data[cmd].append(await self.send_command(cmd, allow_warning=True))
        except APIError:
            pass
        except Exception as e:
            logging.warning(
                f"{self} - ([Hidden] X19 Multicommand) - API Command Error {e}"
            )
        return data

    async def version(self) -> dict:
        """Get miner version info.
        <details>
            <summary>Expand</summary>

        Returns:
            Miner version information.
        </details>
        """
        return await self.send_command("version")

    async def config(self) -> dict:
        """Get some basic configuration info.
        <details>
            <summary>Expand</summary>

        Returns:
            ## Some miner configuration information:
                * ASC Count <- the number of ASCs
                * PGA Count <- the number of PGAs
                * Pool Count <- the number of Pools
                * Strategy <- the current pool strategy
                * Log Interval <- the interval of logging
                * Device Code <- list of compiled device drivers
                * OS <- the current operating system
                * Failover-Only <- failover-only setting
                * Scan Time <- scan-time setting
                * Queue <- queue setting
                * Expiry <- expiry setting
        </details>
        """
        return await self.send_command("config")

    async def summary(self) -> dict:
        """Get the status summary of the miner.
        <details>
            <summary>Expand</summary>

        Returns:
            The status summary of the miner.
        </details>
        """
        return await self.send_command("summary")

    async def pools(self) -> dict:
        """Get pool information.
        <details>
            <summary>Expand</summary>

        Returns:
            Miner pool information.
        </details>
        """
        return await self.send_command("pools")

    async def devs(self) -> dict:
        """Get data on each PGA/ASC with their details.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on each PGA/ASC with their details.
        </details>
        """
        return await self.send_command("devs")

    async def procs(self) -> dict:
        """Get data on each processor with their details.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on each processor with their details.
        </details>
        """
        return await self.send_command("procs")

    async def devscan(self, info: str = "") -> dict:
        """Get data on each processor with their details.
        <details>
            <summary>Expand</summary>

        Parameters:
            info: Info to scan for device by.

        Returns:
            Data on each processor with their details.
        </details>
        """
        return await self.send_command("devscan", parameters=info)

    async def pga(self, n: int) -> dict:
        """Get data from PGA n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The PGA number to get data from.

        Returns:
            Data on the PGA n.
        </details>
        """
        return await self.send_command("pga", parameters=n)

    async def proc(self, n: int = 0) -> dict:
        """Get data processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to get data on.

        Returns:
            Data on processor n.
        </details>
        """
        return await self.send_command("proc", parameters=n)

    async def pgacount(self) -> dict:
        """Get data fon all PGAs.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the PGAs connected.
        </details>
        """
        return await self.send_command("pgacount")

    async def proccount(self) -> dict:
        """Get data fon all processors.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the processors connected.
        </details>
        """
        return await self.send_command("proccount")

    async def switchpool(self, n: int) -> dict:
        """Switch pools to pool n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The pool to switch to.

        Returns:
            A confirmation of switching to pool n.
        </details>
        """
        return await self.send_command("switchpool", parameters=n)

    async def enablepool(self, n: int) -> dict:
        """Enable pool n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The pool to enable.

        Returns:
            A confirmation of enabling pool n.
        </details>
        """
        return await self.send_command("enablepool", parameters=n)

    async def addpool(self, url: str, username: str, password: str) -> dict:
        """Add a pool to the miner.
        <details>
            <summary>Expand</summary>

        Parameters:
            url: The URL of the new pool to add.
            username: The users username on the new pool.
            password: The worker password on the new pool.

        Returns:
            A confirmation of adding the pool.
        </details>
        """
        return await self.send_command(
            "addpool", parameters=f"{url},{username},{password}"
        )

    async def poolpriority(self, *n: int) -> dict:
        """Set pool priority.
        <details>
            <summary>Expand</summary>

        Parameters:
            *n: Pools in order of priority.

        Returns:
            A confirmation of setting pool priority.
        </details>
        """
        pools = f"{','.join([str(item) for item in n])}"
        return await self.send_command("poolpriority", parameters=pools)

    async def poolquota(self, n: int, q: int) -> dict:
        """Set pool quota.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: Pool number to set quota on.
            q: Quota to set the pool to.

        Returns:
            A confirmation of setting pool quota.
        </details>
        """
        return await self.send_command("poolquota", parameters=f"{n},{q}")

    async def disablepool(self, n: int) -> dict:
        """Disable a pool.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: Pool to disable.

        Returns:
            A confirmation of diabling the pool.
        </details>
        """
        return await self.send_command("disablepool", parameters=n)

    async def removepool(self, n: int) -> dict:
        """Remove a pool.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: Pool to remove.

        Returns:
            A confirmation of removing the pool.
        </details>
        """
        return await self.send_command("removepool", parameters=n)

    async def save(self, filename: str = None) -> dict:
        """Save the config.
        <details>
            <summary>Expand</summary>

        Parameters:
            filename: Filename to save the config as.

        Returns:
            A confirmation of saving the config.
        </details>
        """
        if filename:
            return await self.send_command("save", parameters=filename)
        else:
            return await self.send_command("save")

    async def quit(self) -> dict:
        """Quit CGMiner.
        <details>
            <summary>Expand</summary>

        Returns:
            A single "BYE" before CGMiner quits.
        </details>
        """
        return await self.send_command("quit")

    async def notify(self) -> dict:
        """Notify the user of past errors.
        <details>
            <summary>Expand</summary>

        Returns:
            The last status and count of each devices problem(s).
        </details>
        """
        return await self.send_command("notify")

    async def privileged(self) -> dict:
        """Check if you have privileged access.
        <details>
            <summary>Expand</summary>

        Returns:
            The STATUS section with an error if you have no privileged access, or success if you have privileged access.
        </details>
        """
        return await self.send_command("privileged")

    async def pgaenable(self, n: int) -> dict:
        """Enable PGA n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The PGA to enable.

        Returns:
            A confirmation of enabling PGA n.
        </details>
        """
        return await self.send_command("pgaenable", parameters=n)

    async def pgadisable(self, n: int) -> dict:
        """Disable PGA n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The PGA to disable.

        Returns:
            A confirmation of disabling PGA n.
        </details>
        """
        return await self.send_command("pgadisable", parameters=n)

    async def pgarestart(self, n: int) -> dict:
        """Restart PGA n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The PGA to restart.

        Returns:
            A confirmation of restarting PGA n.
        </details>
        """
        return await self.send_command("pgadisable", parameters=n)

    async def pgaidentify(self, n: int) -> dict:
        """Identify PGA n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The PGA to identify.

        Returns:
            A confirmation of identifying PGA n.
        </details>
        """
        return await self.send_command("pgaidentify", parameters=n)

    async def procenable(self, n: int) -> dict:
        """Enable processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to enable.

        Returns:
            A confirmation of enabling processor n.
        </details>
        """
        return await self.send_command("procenable", parameters=n)

    async def procdisable(self, n: int) -> dict:
        """Disable processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to disable.

        Returns:
            A confirmation of disabling processor n.
        </details>
        """
        return await self.send_command("procdisable", parameters=n)

    async def procrestart(self, n: int) -> dict:
        """Restart processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to restart.

        Returns:
            A confirmation of restarting processor n.
        </details>
        """
        return await self.send_command("procdisable", parameters=n)

    async def procidentify(self, n: int) -> dict:
        """Identify processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to identify.

        Returns:
            A confirmation of identifying processor n.
        </details>
        """
        return await self.send_command("procidentify", parameters=n)

    async def devdetails(self) -> dict:
        """Get data on all devices with their static details.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on all devices with their static details.
        </details>
        """
        return await self.send_command("devdetails")

    async def restart(self) -> dict:
        """Restart CGMiner using the API.
        <details>
            <summary>Expand</summary>

        Returns:
            A reply informing of the restart.
        </details>
        """
        return await self.send_command("restart")

    async def stats(self) -> dict:
        """Get stats of each device/pool with more than 1 getwork.
        <details>
            <summary>Expand</summary>

        Returns:
            Stats of each device/pool with more than 1 getwork.
        </details>
        """
        return await self.send_command("stats")

    async def check(self, command: str) -> dict:
        """Check if the command command exists in CGMiner.
        <details>
            <summary>Expand</summary>

        Parameters:
            command: The command to check.

        Returns:
            ## Information about a command:
                * Exists (Y/N) <- the command exists in this version
                * Access (Y/N) <- you have access to use the command
        </details>
        """
        return await self.send_command("check", parameters=command)

    async def failover_only(self, failover: bool) -> dict:
        """Set failover-only.
        <details>
            <summary>Expand</summary>

        Parameters:
            failover: What to set failover-only to.

        Returns:
            Confirmation of setting failover-only.
        </details>
        """
        return await self.send_command("failover-only", parameters=failover)

    async def coin(self) -> dict:
        """Get information on the current coin.
        <details>
            <summary>Expand</summary>

        Returns:
            ## Information about the current coin being mined:
                * Hash Method <- the hashing algorithm
                * Current Block Time <- blocktime as a float, 0 means none
                * Current Block Hash <- the hash of the current block, blank means none
                * LP <- whether LP is in use on at least 1 pool
                * Network Difficulty: the current network difficulty
        </details>
        """
        return await self.send_command("coin")

    async def debug(self, setting: str) -> dict:
        """Set a debug setting.
        <details>
            <summary>Expand</summary>

        Parameters:
            setting: Which setting to switch to.
                ## Options are:
                    * Silent
                    * Quiet
                    * Verbose
                    * Debug
                    * RPCProto
                    * PerDevice
                    * WorkTime
                    * Normal

        Returns:
            Data on which debug setting was enabled or disabled.
        </details>
        """
        return await self.send_command("debug", parameters=setting)

    async def setconfig(self, name: str, n: int) -> dict:
        """Set config of name to value n.
        <details>
            <summary>Expand</summary>

        Parameters:
            name: The name of the config setting to set.
                ## Options are:
                    * queue
                    * scantime
                    * expiry
            n: The value to set the 'name' setting to.

        Returns:
            The results of setting config of name to n.
        </details>
        """
        return await self.send_command("setconfig", parameters=f"{name},{n}")

    async def pgaset(self, n: int, opt: str, val: int = None) -> dict:
        """Set PGA option opt to val on PGA n.
        <details>
            <summary>Expand</summary>

        Options:
        ```
            MMQ -
                opt: clock
                val: 2 - 250 (multiple of 2)
            XBS -
                opt: clock
                val: 2 - 250 (multiple of 2)
        ```

        Parameters:
            n: The PGA to set the options on.
            opt: The option to set. Setting this to 'help' returns a help message.
            val: The value to set the option to.

        Returns:
            Confirmation of setting PGA n with opt[,val].
        </details>
        """
        if val:
            return await self.send_command("pgaset", parameters=f"{n},{opt},{val}")
        else:
            return await self.send_command("pgaset", parameters=f"{n},{opt}")

    async def pprocset(self, n: int, opt: str, val: int = None) -> dict:
        """Set processor option opt to val on processor n.
        <details>
            <summary>Expand</summary>

        Options:
        ```
            MMQ -
                opt: clock
                val: 2 - 250 (multiple of 2)
            XBS -
                opt: clock
                val: 2 - 250 (multiple of 2)
        ```

        Parameters:
            n: The PGA to set the options on.
            opt: The option to set. Setting this to 'help' returns a help message.
            val: The value to set the option to.

        Returns:
            Confirmation of setting PGA n with opt[,val].
        </details>
        """
        if val:
            return await self.send_command("pgaset", parameters=f"{n},{opt},{val}")
        else:
            return await self.send_command("pgaset", parameters=f"{n},{opt}")

    async def zero(self, which: str, summary: bool) -> dict:
        """Zero a device.
        <details>
            <summary>Expand</summary>

        Parameters:
            which: Which device to zero. Setting this to 'all' zeros all devices. Setting this to 'bestshare' zeros only the bestshare values for each pool and global.
            summary: Whether or not to show a full summary.


        Returns:
            the STATUS section with info on the zero and optional summary.
        </details>
        """
        return await self.send_command("zero", parameters=f"{which},{summary}")

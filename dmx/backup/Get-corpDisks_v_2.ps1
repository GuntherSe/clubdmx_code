
<#.Synopsis
Gets disk information for computer(s)

.Description
Given computer name or string arrayy from computer names, the script will try to connect remotely using best method and gets disk information.
The script is using Get-WmiObject to get remote wmi data. I recommend that you look at my Get-CorpCimInfo to replace Get-WmiObject.Get-CorpCimInfo will try to get wmi data using CIM Sessions, if it fails, it will try PowerShell Remoting, if it fails, it will try DCOM. you can find more about this function here http://wp.me/p1eUZH-kq

Expected return value is a unique object per remote computer. The returned object per remote computer has two properties:

  - Computername : computer name for the computer being queried.

  - diskinfo     : array of objects. Each object represents logical disk with following properties:

           - VolumeName : i.e (OS)
           - Drive      : i.e (C:)
           - SizeGB
           - FreeGB
           - FreePercentage 

Why this is a unique script ?
Two reasons. First, it returns an object not an exception in case of failing to get wmi data.Second,it will return object per computer not per disk. Read more here at http://ammarhasayen.com‎ 


.PARAMETER Computername
Can accpet string array of computer names or single computer name. Aliases for this parameter are "name","machinename","computer","host","hostname","machine". Default value for this parameter is localhost.



.Example
Getting disk info from computer PC1
PS C:\>Get-CorpDisks -ComputerName "PC1"

.Example
Get computer names from text file and pipeline the output to Get-CorpDisks
PS C:\> get-content computers.txt | Get-CorpDisks

.INPUTS 
System.String 


.Notes
Last Updated             : Nov 13, 2013
Version                  : 1.0 
Author                   : Ammar Hasayen (@ammarhasayen)


.Link
http://ammarhasayen.com
http://wp.me/p1eUZH-kq


#>

[cmdletbinding()]

    Param(
    # parameters for function Get-corpDisks

    [Parameter(Position = 0,
               ValueFromPipeline = $true,
               ValueFromPipelineByPropertyName = $true)]

    [alias("name","machinename","computer","host","hostname","machine")]

    [string[]]$Computername=$env:computername
    )


    Begin { 
    # Begin block for function Get-corpDisks

        Write-Verbose -Message "Starting $($MyInvocation.Mycommand)"  

        Write-verbose -Message ($PSBoundParameters | out-string)


    } # function Get-CorpDisks Begin Section

    

    Process{
    # Process block for function Get-corpDisks



        Foreach ($Computer in $ComputerName) { 
             
            Write-Verbose -Message "ComputerName: $Computer - Getting disk info." 
            
            try { 
                # Set all the parameters required for our query 
                $params = @{'ComputerName'   = $Computer; 
                            'Class'          = 'Win32_LogicalDisk'; 
                            'Filter'         = "DriveType=2"
                            'ErrorAction'    = 'Stop'}
                             
                $compHealthy = $true
                                
                # Run the query against the current $Computer     
                $Disks = Get-WmiObject @params 

            }# Try 
             
            Catch { 

                Write-Verbose -Message "ComputerName: $Computer - Error while getting disk info"

                $compHealthy = $false

            }# Catch 

            # creating custome object to output
            
            $outobjparam = @{'computername' = $Computer}

            if ($compHealthy) { 

                Write-Verbose -Message "ComputerName: $Computer - Formating information for each disk(s)" 

                [array]$compdisks =  @()

                foreach ($disk in $Disks) { 
                     
                    # Prepare the Information output 
                    Write-Verbose -Message "ComputerName: $Computer - $($Disk.deviceid)" 
                    $disktemplate = @{'Drive'         =$disk.deviceid; 
                                      'VolumeName'    = $disk.VolumeName; 
                                      'SizeGB'        =("{0:N2}" -f($disk.size/1GB));   
                                      'FreeGB'        =("{0:N2}" -f($disk.freespace/1GB));                                    
                                      'FreePercentage'=("{0:P2}" -f(($disk.Freespace/1GB) / ($disk.Size/1GB)))} 
                     
                    # Create a new PowerShell object for the disk  
                    $objectdisk = New-Object -TypeName PSObject -Property $disktemplate 
                    
                    $compdisks += $objectdisk                     
                     
                                        
                }# foreach ($disk in $disks) 

                $outobjparam.add('disks', $compdisks)
                 
            }# if ($comphealthy) 

            else { # else if ($comphealthy) 

            $outobjparam.add('disks', 'n/a')

            }

            $finaloutput = New-Object -TypeName psobject -Property $outobjparam

            Write-Output -InputObject  $finaloutput

             
        }#Foreach ($Computer in $ComputerName)

        Write-Verbose -Message "ComputerName: $Computer - Finish processing." 

    } #function Get-CorpDisks Process Section



    End{
    # End block for function Get-corpDisks
    } #function Get-CorpDisks End Section











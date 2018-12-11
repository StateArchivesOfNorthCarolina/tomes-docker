@if "%DEBUG%" == "" @echo off
@rem ##########################################################################
@rem
@rem  TOMES Startup using docker-compose
@rem
@rem ##########################################################################

docker-compose -f .\docker-compose__WINDOWS.yml up

all: mtruntime

mtruntime: mtruntime.c rules.h
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ mtruntime.c

clean:
	$(RM) mtruntime
